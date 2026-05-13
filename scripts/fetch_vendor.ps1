# fetch_vendor.ps1 — скачать Three.js в web/js/vendor/ (нужно один раз)
# Использование: .\scripts\fetch_vendor.ps1

$root    = Split-Path $PSScriptRoot -Parent
$vendor  = "$root\web\js\vendor"
$addons  = "$vendor\addons"
$base    = "https://cdn.jsdelivr.net/npm/three@0.165.0"

New-Item -ItemType Directory -Force -Path "$addons\controls", "$addons\loaders" | Out-Null

$files = @{
    "$vendor\three.module.js"                = "$base/build/three.module.js"
    "$addons\controls\OrbitControls.js"      = "$base/examples/jsm/controls/OrbitControls.js"
    "$addons\controls\TransformControls.js"  = "$base/examples/jsm/controls/TransformControls.js"
    "$addons\loaders\PLYLoader.js"           = "$base/examples/jsm/loaders/PLYLoader.js"
}

foreach ($dst in $files.Keys) {
    $src = $files[$dst]
    Write-Host "Downloading $(Split-Path $dst -Leaf)..."
    Invoke-WebRequest -Uri $src -OutFile $dst -UseBasicParsing
}

Write-Host "Done. Three.js vendored to web\js\vendor\"
