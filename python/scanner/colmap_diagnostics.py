"""Diagnostics and preprocessing for COLMAP input images."""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# Empirical base times (seconds) per unit at 1 Mpx, quality=low
_TIME_FEAT_PER_IMAGE_PER_MPX   = 0.5   # feature extraction
_TIME_MATCH_PER_PAIR            = 0.008  # exhaustive matching
_TIME_SPARSE_PER_IMAGE          = 3.0   # mapper
_TIME_DENSE_PER_IMAGE_PER_MPX2  = 1.5   # patch_match_stereo (per Mpx^2 proxy)

_QUALITY_ITERS = {"low": 3, "medium": 5, "high": 7}
_QUALITY_GEOM  = {"low": 1, "medium": 2, "high": 2}   # geom_consistency multiplier


def diagnose_images(image_dir: Path) -> dict:
    """
    Scan image_dir, print per-image info and warnings about resolution.
    Returns a dict with summary statistics.
    """
    try:
        from PIL import Image as PilImage
    except ImportError:
        raise RuntimeError("Pillow not installed: pip install pillow")

    image_dir = Path(image_dir)
    files = sorted(
        f for f in image_dir.iterdir()
        if f.is_file() and f.suffix.lower() in _IMAGE_EXTS
    )
    if not files:
        print(f"No images found in {image_dir}")
        return {}

    print(f"\n=== Image Diagnostics: {image_dir} ({len(files)} images) ===")

    widths, heights, sizes_mb = [], [], []
    for f in files:
        mb = f.stat().st_size / 1_000_000
        with PilImage.open(f) as img:
            w, h = img.size
        widths.append(w)
        heights.append(h)
        sizes_mb.append(mb)
        mpx = w * h / 1_000_000
        print(f"  {f.name:<24}  {w}x{h}  ({mpx:.1f} Mpx)  {mb:.1f} MB")

    avg_w    = int(sum(widths)  / len(widths))
    avg_h    = int(sum(heights) / len(heights))
    total_mb = sum(sizes_mb)
    avg_mpx  = avg_w * avg_h / 1_000_000
    n        = len(files)

    print(f"\n  Images  : {n}")
    print(f"  Avg res : {avg_w}x{avg_h}  ({avg_mpx:.1f} Mpx)")
    print(f"  Total   : {total_mb:.0f} MB")

    if avg_mpx > 4.0:
        patch_ops = avg_mpx * n * 5 * 2   # medium: 5 iters, geom_consistency
        print()
        print("  [WARNING] Photos are very large!")
        print(f"  {avg_w}x{avg_h} = {avg_mpx:.0f} Mpx x {n} images x 5 iter x 2 passes")
        print(f"  = {patch_ops:.0f} M pixel-iterations in PatchMatchStereo")
        print(f"  This is the reason for 2+ hours of processing.")
        print()

        recommended = _recommend_max_size(avg_w, avg_h)
        ratio = recommended / max(avg_w, avg_h)
        rw, rh = int(avg_w * ratio), int(avg_h * ratio)
        saved = (1 - ratio ** 2) * 100
        print(f"  Recommendation:")
        print(f"    max_image_size={recommended}  ->  ~{rw}x{rh} ({rw*rh/1e6:.1f} Mpx)")
        print(f"    Speed-up: ~{int(1/ratio**2)}x  (saves {saved:.0f}% of compute)")
        print(f"    COLMAP keeps full-res for feature extraction geometry,")
        print(f"    only resizes internally for depth map computation.")
    else:
        print("  Resolution OK for COLMAP.")

    print()
    return {
        "n_images": n,
        "avg_w": avg_w,
        "avg_h": avg_h,
        "avg_mpx": avg_mpx,
        "total_mb": total_mb,
        "files": files,
    }


def resize_images(
    image_dir: Path,
    output_dir: Path,
    max_size: int = 1600,
) -> dict:
    """
    Copy images resized to max_size on the long side, preserving EXIF.
    COLMAP uses focal length from EXIF — must be preserved.
    Returns summary dict.
    """
    try:
        from PIL import Image as PilImage
        import piexif
        _HAS_PIEXIF = True
    except ImportError:
        _HAS_PIEXIF = False
        try:
            from PIL import Image as PilImage
        except ImportError:
            raise RuntimeError("Pillow not installed: pip install pillow")

    image_dir  = Path(image_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        f for f in image_dir.iterdir()
        if f.is_file() and f.suffix.lower() in _IMAGE_EXTS
    )
    if not files:
        print(f"No images in {image_dir}")
        return {}

    print(f"\n=== Resize: {image_dir} -> {output_dir}  (max_size={max_size}) ===")

    total_saved_mb = 0.0
    results = []
    for f in files:
        orig_mb = f.stat().st_size / 1_000_000
        with PilImage.open(f) as img:
            orig_w, orig_h = img.size
            long_side = max(orig_w, orig_h)

            if long_side <= max_size:
                # No resize needed, just copy
                out_path = output_dir / f.name
                out_path.write_bytes(f.read_bytes())
                print(f"  {f.name:<24}  {orig_w}x{orig_h} -> (unchanged)  {orig_mb:.1f} MB")
                results.append({"file": out_path, "orig": (orig_w, orig_h),
                                 "new": (orig_w, orig_h)})
                continue

            scale = max_size / long_side
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)

            # Read EXIF before resizing
            exif_bytes = None
            if _HAS_PIEXIF:
                try:
                    exif_dict = piexif.load(str(f))
                    exif_bytes = piexif.dump(exif_dict)
                except Exception:
                    pass
            elif hasattr(img, "info") and "exif" in img.info:
                exif_bytes = img.info["exif"]

            img_rgb = img.convert("RGB")
            resized = img_rgb.resize((new_w, new_h), PilImage.LANCZOS)

            out_path = output_dir / f.name
            save_kwargs: dict = {"quality": 92, "optimize": False}
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes
            resized.save(out_path, **save_kwargs)

        new_mb = out_path.stat().st_size / 1_000_000
        saved  = orig_mb - new_mb
        total_saved_mb += saved
        print(f"  {f.name:<24}  {orig_w}x{orig_h} -> {new_w}x{new_h}"
              f"  {orig_mb:.1f} -> {new_mb:.1f} MB  (-{saved:.1f} MB)")
        results.append({"file": out_path, "orig": (orig_w, orig_h),
                         "new": (new_w, new_h)})

    print(f"\n  Done: {len(results)} images  saved {total_saved_mb:.0f} MB total")
    print(f"  Output: {output_dir}")
    return {"output_dir": output_dir, "files": results, "saved_mb": total_saved_mb}


_QUALITY_PMS_MAX_PX = {"low": 800, "medium": 1200, "high": 1600}


def estimate_time(n_images: int, avg_resolution: int, quality: str = "low") -> str:
    """
    Rough time estimate for COLMAP pipeline.
    avg_resolution: long side of original images in pixels (e.g. 5616).
    Uses actual PatchMatchStereo.max_image_size from quality profile.
    """
    # Feature extraction uses FeatureExtraction.max_image_size (still large-ish)
    feat_px  = min(avg_resolution, {"low": 1000, "medium": 1600, "high": 2400}.get(quality, 1000))
    feat_mpx = (feat_px * feat_px * 0.75) / 1_000_000

    # PatchMatchStereo uses pms_max_image_size (capped)
    pms_px   = min(avg_resolution, _QUALITY_PMS_MAX_PX.get(quality, 800))
    pms_mpx  = (pms_px * pms_px * 0.75) / 1_000_000

    iters    = _QUALITY_ITERS.get(quality, 3)
    geom_mul = _QUALITY_GEOM.get(quality, 1)

    t_feat   = _TIME_FEAT_PER_IMAGE_PER_MPX * n_images * feat_mpx
    t_match  = _TIME_MATCH_PER_PAIR * n_images * n_images
    t_sparse = _TIME_SPARSE_PER_IMAGE * n_images
    t_dense  = _TIME_DENSE_PER_IMAGE_PER_MPX2 * n_images * pms_mpx * iters * geom_mul

    total_sec = t_feat + t_match + t_sparse + t_dense
    total_min = total_sec / 60.0

    lines = [
        f"Estimated time (quality={quality}, {n_images} images @ {avg_resolution}px):",
        f"  Feature extraction : {t_feat/60:.1f} min  (feat_size={feat_px}px)",
        f"  Matching           : {t_match/60:.1f} min",
        f"  Sparse (mapper)    : {t_sparse/60:.1f} min",
        f"  Dense (MVS)        : {t_dense/60:.1f} min"
        f"  (pms_size={pms_px}px, {iters} iter x {geom_mul} pass)",
        f"  ----------------------------------------",
        f"  TOTAL              : ~{total_min:.0f} min",
    ]
    result = "\n".join(lines)
    print(result)
    return result


def _recommend_max_size(w: int, h: int) -> int:
    """Choose max_image_size so depth maps are under 2 Mpx."""
    long = max(w, h)
    if long <= 1600:
        return long
    # Target: long side ≤ 1200 for 'medium', ≤ 800 for 'low'
    # Default recommendation: keep it under 1600 for reasonable speed
    return 1200
