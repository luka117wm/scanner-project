---
created: 2026-04-19T05:36:48 (UTC +03:00)
tags: []
source: https://en.wikipedia.org/wiki/STL_(file_format)
author: Contributors to Wikimedia projects
---

# STL (file format) - Wikipedia

> ## Excerpt
> From Wikipedia, the free encyclopedia

---
From Wikipedia, the free encyclopedia

| STL |
| --- |
| [![](https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/The_differences_between_CAD_and_STL_Models.svg/330px-The_differences_between_CAD_and_STL_Models.svg.png)](https://en.wikipedia.org/wiki/File:The_differences_between_CAD_and_STL_Models.svg)
A CAD representation of a [torus](https://en.wikipedia.org/wiki/Torus "Torus") (shown as two concentric red circles) and an STL approximation of the same shape (composed of triangular planes)

 |
| [Filename extension](https://en.wikipedia.org/wiki/Filename_extension "Filename extension") | 

.stl

 |
| [Internet media type](https://en.wikipedia.org/wiki/Media_type "Media type") | 

-   `model/stl`<sup id="cite_ref-1"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-1"><span>[</span>1<span>]</span></a></sup><sup id="cite_ref-loc_2-0"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-loc-2"><span>[</span>2<span>]</span></a></sup>
-   `model/x.stl-ascii`
-   `model/x.stl-binary`



 |
| Developed by | [3D Systems](https://en.wikipedia.org/wiki/3D_Systems "3D Systems") |
| Initial release | 1987 |
| Type of format | [Stereolithography](https://en.wikipedia.org/wiki/Stereolithography "Stereolithography") |

**STL** is a [file format](https://en.wikipedia.org/wiki/File_format "File format") native to the [stereolithography](https://en.wikipedia.org/wiki/Stereolithography "Stereolithography") [CAD](https://en.wikipedia.org/wiki/Computer-aided_design "Computer-aided design") software created by [3D Systems](https://en.wikipedia.org/wiki/3D_Systems "3D Systems").<sup id="cite_ref-3"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-3"><span>[</span>3<span>]</span></a></sup><sup id="cite_ref-4"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-4"><span>[</span>4<span>]</span></a></sup><sup id="cite_ref-5"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-5"><span>[</span>5<span>]</span></a></sup> [Chuck Hull](https://en.wikipedia.org/wiki/Chuck_Hull "Chuck Hull"), the inventor of stereolithography and 3D Systems’ founder, reports that the file extension is an abbreviation for _stereolithography_,<sup id="cite_ref-6"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-6"><span>[</span>6<span>]</span></a></sup> although it is also referred to as _standard triangle language_ or _standard tessellation language_.<sup id="cite_ref-loc_2-1"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-loc-2"><span>[</span>2<span>]</span></a></sup>

An STL file describes a raw, unstructured [triangulated](https://en.wikipedia.org/wiki/Triangulation_(geometry) "Triangulation (geometry)") surface by the [unit](https://en.wikipedia.org/wiki/Unit_vector "Unit vector") [normal](https://en.wikipedia.org/wiki/Surface_normal "Surface normal") and vertices (ordered by the [right-hand rule](https://en.wikipedia.org/wiki/Right-hand_rule "Right-hand rule")<sup id="cite_ref-loc_2-2"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-loc-2"><span>[</span>2<span>]</span></a></sup>) of the triangles using a three-dimensional [Cartesian coordinate system](https://en.wikipedia.org/wiki/Cartesian_coordinate_system "Cartesian coordinate system").<sup id="cite_ref-burkardt_7-0"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-burkardt-7"><span>[</span>7<span>]</span></a></sup> In the original specification, all STL coordinates were required to be positive numbers, but this restriction is no longer enforced and negative coordinates are commonly encountered in STL files today. STL files contain no scale information, and the units are arbitrary.<sup id="cite_ref-fabbers_8-0"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-fabbers-8"><span>[</span>8<span>]</span></a></sup> STL files describe only the surface geometry of a three-dimensional object without any representation of color, texture or other common CAD model attributes. The STL format specifies both [ASCII](https://en.wikipedia.org/wiki/ASCII "ASCII") and [binary](https://en.wikipedia.org/wiki/Binary_file "Binary file") representations. Binary files are more common, since they are more compact.<sup id="cite_ref-burns_9-0"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-burns-9"><span>[</span>9<span>]</span></a></sup><sup>[<i><a href="https://en.wikipedia.org/wiki/Wikipedia:Accuracy_dispute#Disputed_statement" title="Wikipedia:Accuracy dispute"><span title="The material near this tag is possibly inaccurate or nonfactual. (March 2026)">dubious</span></a> – <a href="https://en.wikipedia.org/wiki/Talk:STL_(file_format)#Dubious" title="Talk:STL (file format)">discuss</a></i>]</sup>

STL is widely used for [rapid prototyping](https://en.wikipedia.org/wiki/Rapid_prototyping "Rapid prototyping"), [3D printing](https://en.wikipedia.org/wiki/3D_printing "3D printing") and [computer-aided manufacturing](https://en.wikipedia.org/wiki/Computer-aided_manufacturing "Computer-aided manufacturing"),<sup id="cite_ref-10"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-10"><span>[</span>10<span>]</span></a></sup> and supported by many other software packages.<sup>[<i><a href="https://en.wikipedia.org/wiki/Wikipedia:Citation_needed" title="Wikipedia:Citation needed"><span title="This claim needs references to reliable sources. (June 2023)">citation needed</span></a></i>]</sup>

STL was invented by the Albert Consulting Group for [3D Systems](https://en.wikipedia.org/wiki/3D_Systems "3D Systems") in 1987.<sup id="cite_ref-All3DP_11-0"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-All3DP-11"><span>[</span>11<span>]</span></a></sup> The format was developed for 3D Systems' first commercial 3D printers. Since its initial release, the format remained relatively unchanged for 22 years.<sup id="cite_ref-stl2_12-0"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-stl2-12"><span>[</span>12<span>]</span></a></sup>

In 2009, an update to the format dubbed STL 2.0 was proposed, which evolved into the [additive manufacturing file format](https://en.wikipedia.org/wiki/Additive_manufacturing_file_format "Additive manufacturing file format").<sup id="cite_ref-stl2_12-1"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-stl2-12"><span>[</span>12<span>]</span></a></sup><sup id="cite_ref-13"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-13"><span>[</span>13<span>]</span></a></sup>

An ASCII STL file begins with the line:

```
solid name

```

where name is an optional string (though if name is omitted there must still be a space after solid, for compatibility with some software). The remainder of the line is ignored and is sometimes used to store metadata (e.g., filename, author, modification date, etc).<sup id="cite_ref-14"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-14"><span>[</span>14<span>]</span></a></sup> The file continues with any number of triangles, each represented as follows:<sup id="cite_ref-15"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-15"><span>[</span>15<span>]</span></a></sup>

```
facet normal ni nj nk
    outer loop
        vertex v1x v1y v1z
        vertex v2x v2y v2z
        vertex v3x v3y v3z
    endloop
endfacet

```

where each n or v is a [floating-point number](https://en.wikipedia.org/wiki/Floating-point_number "Floating-point number") in sign\-[mantissa](https://en.wikipedia.org/wiki/Significand "Significand")\-`e`\-sign\-[exponent](https://en.wikipedia.org/wiki/Exponent "Exponent") format, e.g., `2.648000e-002`. The file concludes with:

```
endsolid name

```

[![](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Sphericon.stl/250px-Sphericon.stl.png)](https://en.wikipedia.org/wiki/File:Sphericon.stl)

An example [ASCII STL](https://upload.wikimedia.org/wikipedia/commons/b/b1/Sphericon.stl) of a [sphericon](https://en.wikipedia.org/wiki/Sphericon "Sphericon")

The structure of the format suggests that other possibilities exist (e.g., facets with more than one `loop`, or loops with more than three vertices), although the file format description refers only to triangle [tessellations](https://en.wikipedia.org/wiki/Tessellation "Tessellation").<sup id="cite_ref-loc_2-3"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-loc-2"><span>[</span>2<span>]</span></a></sup>

[Whitespace](https://en.wikipedia.org/wiki/Whitespace_character "Whitespace character") (spaces, tabs, newlines) may be used anywhere in the file except within numbers or words. The spaces between `facet` and `normal` and between `outer` and `loop` are required.<sup id="cite_ref-burns_9-1"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-burns-9"><span>[</span>9<span>]</span></a></sup>

Because ASCII STL files can be large, a binary version of STL exists. A binary STL file has an 80-character header that is generally ignored, but should never begin with the ASCII representation of the string `solid`, as that may lead some software to confuse it with an ASCII STL file. Following the header is a 4-byte [little-endian](https://en.wikipedia.org/wiki/Little-endian "Little-endian") unsigned integer indicating the number of triangular facets in the file. Following that is data describing each triangle in turn. The file simply ends after the last triangle.

Each triangle is described by 12 32-bit floating-point numbers: 3 for the normal and then 3 for the X/Y/Z coordinate of each vertex – just as with the ASCII version of STL. After these follows a 2-byte ("short") unsigned integer that is the "attribute byte count" – in the standard format, this should be zero because most software does not understand anything else.<sup id="cite_ref-burns_9-2"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-burns-9"><span>[</span>9<span>]</span></a></sup>

Floating-point numbers are represented as [IEEE floating-point](https://en.wikipedia.org/wiki/IEEE_floating-point "IEEE floating-point") numbers and are assumed to be [little-endian](https://en.wikipedia.org/wiki/Little-endian "Little-endian"), although this is not stated in documentation.

```
UINT8[80]    – Header                 - 80 bytes
UINT32       – Number of triangles    - 04 bytes
foreach triangle                      - 50 bytes
    REAL32[3] – Normal vector         - 12 bytes
    REAL32[3] – Vertex 1              - 12 bytes
    REAL32[3] – Vertex 2              - 12 bytes
    REAL32[3] – Vertex 3              - 12 bytes
    UINT16    – Attribute byte count  - 02 bytes
end

```

There are at least two non-standard variations on the binary STL format for adding color information:

-   The VisCAM and SolidView software packages use the two "attribute byte count" bytes at the end of every triangle to store a 15-bit [RGB](https://en.wikipedia.org/wiki/RGB "RGB") color:
    -   bits 0–4 are the intensity level for blue (0–31),
    -   bits 5–9 are the intensity level for green (0–31),
    -   bits 10–14 are the intensity level for red (0–31),
    -   bit 15 is 1 if the color is valid, or 0 if the color is not valid (as with normal STL files).
-   The Materialise Magics software uses the 80-byte header at the top of the file to represent the overall color of the entire part. If color is used, then somewhere in the header should be the [ASCII](https://en.wikipedia.org/wiki/ASCII "ASCII") string `COLOR=` followed by four bytes representing red, green, blue and [alpha channel](https://en.wikipedia.org/wiki/Alpha_channel "Alpha channel") (transparency) in the range 0–255. This is the color of the entire object, unless overridden at each facet. Magics also recognizes a material description; a more detailed surface characteristic. Just after `COLOR=RGBA` specification should be another ASCII string `,MATERIAL=` followed by three colors (3×4 bytes): first is a color of [diffuse reflection](https://en.wikipedia.org/wiki/Diffuse_reflection "Diffuse reflection"), second is a color of [specular highlight](https://en.wikipedia.org/wiki/Specular_highlight "Specular highlight"), and third is an [ambient light](https://en.wikipedia.org/wiki/Shading#Ambient_lighting "Shading"). Material settings are preferred over color. The per-facet color is represented in the two "attribute byte count" bytes as follows:
    -   bits 0–4 are the intensity level for red (0–31),
    -   bits 5–9 are the intensity level for green (0–31),
    -   bits 10–14 are the intensity level for blue (0–31),
    -   bit 15 is 0 if this facet has its own unique color, or 1 if the per-object color is to be used.

The red/green/blue ordering within those two bytes is reversed in these two approaches – so while these formats could easily have been compatible, the reversal of the order of the colors means that they are not – and worse still, a generic STL file reader cannot automatically distinguish between them. There is also no way to have facets be selectively transparent because there is no per-facet alpha value – although in the context of current rapid prototyping machinery, this is not important.

In both ASCII and binary versions of STL, the [facet normal](https://en.wikipedia.org/wiki/Normal_(geometry) "Normal (geometry)") should be a [unit vector](https://en.wikipedia.org/wiki/Unit_vector "Unit vector") pointing outward from the solid object.<sup id="cite_ref-16"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-16"><span>[</span>16<span>]</span></a></sup> In most software this may be set to (0,0,0), and the software automatically calculates a normal based on the order of the triangle vertices using the "[right-hand rule](https://en.wikipedia.org/wiki/Right-hand_rule "Right-hand rule")", i.e. the vertices are listed in counter-clock-wise order from outside.<sup id="cite_ref-loc_2-4"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-loc-2"><span>[</span>2<span>]</span></a></sup> Some STL loaders (e.g. the STL plugin for Art of Illusion) check that the normal in the file agrees with the normal they calculate using the right-hand rule and warn the user when it does not. Other software may ignore the facet normal entirely and use only the right-hand rule. Although it is rare to specify a normal that cannot be calculated using the right-hand rule, in order to be entirely portable, a file should both provide the facet normal and order the vertices appropriately. A notable exception is [SolidWorks](https://en.wikipedia.org/wiki/SolidWorks "SolidWorks"), which uses the normal for [shading effects](https://en.wikipedia.org/wiki/Shading "Shading").

It is not possible to use triangles to perfectly represent curved surfaces. To compensate, users often save enormous STL files to reduce the inaccuracy. However, native formats associated with many 3D design applications use [mathematical surfaces](https://en.wikipedia.org/wiki/Surface_(topology) "Surface (topology)") to preserve detail losslessly in small files. For example, [Rhino 3D](https://en.wikipedia.org/wiki/Rhino_3d "Rhino 3d")<sup id="cite_ref-17"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-17"><span>[</span>17<span>]</span></a></sup> and [Blender](https://en.wikipedia.org/wiki/Blender_(software) "Blender (software)")<sup id="cite_ref-18"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-18"><span>[</span>18<span>]</span></a></sup> implement [NURBS](https://en.wikipedia.org/wiki/Nurbs "Nurbs") to create true curved surfaces and store them in their respective native file formats, but must generate a triangle mesh when exporting a model to the STL format.

[![](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Wikipedia_puzzle_globe_3D_render.stl/250px-Wikipedia_puzzle_globe_3D_render.stl.png)](https://en.wikipedia.org/wiki/File:Wikipedia_puzzle_globe_3D_render.stl)

Wikipedia logo

[3D printers](https://en.wikipedia.org/wiki/3D_printing "3D printing") build objects by solidifying ([SLA](https://en.wikipedia.org/wiki/Stereolithography "Stereolithography"), [SLS](https://en.wikipedia.org/wiki/Selective_laser_sintering "Selective laser sintering"), [SHS](https://en.wikipedia.org/wiki/Selective_heat_sintering "Selective heat sintering"), [DMLS](https://en.wikipedia.org/wiki/Selective_laser_melting "Selective laser melting"), [EBM](https://en.wikipedia.org/wiki/Electron-beam_additive_manufacturing "Electron-beam additive manufacturing"), [DLP](https://en.wikipedia.org/wiki/Digital_Light_Processing "Digital Light Processing")) or printing (3DP, MJM, [FDM](https://en.wikipedia.org/wiki/Fused_filament_fabrication "Fused filament fabrication"), [FFF](https://en.wikipedia.org/wiki/Fused_filament_fabrication "Fused filament fabrication"), PJP, MJS)<sup id="cite_ref-19"><a href="https://en.wikipedia.org/wiki/STL_(file_format)#cite_note-19"><span>[</span>19<span>]</span></a></sup> one layer at a time. This requires a series of closed 2D contours (horizontal layers) that are filled in with solidified material as the layers are fused together. A natural file format for such a machine would be a series of closed polygons (layers or slices) corresponding to different Z-values. However, since it is possible to vary the layer thicknesses for a faster though less precise build, it was easier to define the model to be built as a closed [polyhedron](https://en.wikipedia.org/wiki/Polyhedron "Polyhedron") that can be sliced at the necessary horizontal levels. An incorrect facet normal can affect the way a file is sliced and filled. A slice at a different Z-value can be chosen to miss a bad facet or the file must be returned to CAD program to make corrections and then regenerate the STL file.

To properly form a 3D volume, the surface represented by any STL files must be closed (no holes or reversed vector normal) and connected, where every edge is shared by exactly two faces, and not self-intersecting. Since the STL syntax does not enforce this property, it can be ignored for applications where the void does not matter. The missing surface matters insofar as the software that slices the triangles requires it to ensure that the resulting 2D polygons are closed. Sometimes such software can be written to clean up small discrepancies by moving vertices that are close together so that they coincide. The results are not predictable, and may require repair using another program. Vector 3D printers require a clean STL file and printing a bad data file either fails to fill or may stop printing.

[![](https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Utah_teapot_%28solid%29.stl/250px-Utah_teapot_%28solid%29.stl.png)](https://en.wikipedia.org/wiki/File:Utah_teapot_(solid).stl)

[STL model](https://upload.wikimedia.org/wikipedia/commons/9/93/Utah_teapot_%28solid%29.stl) of the [Utah teapot](https://en.wikipedia.org/wiki/Utah_teapot "Utah teapot")

STL is simple and easy to output. Consequently, many [computer-aided design](https://en.wikipedia.org/wiki/Computer-aided_design "Computer-aided design") systems can output the STL file format. Although the output is simple to produce, mesh connectivity information is discarded because the identity of shared vertices is lost.

Many [computer-aided manufacturing](https://en.wikipedia.org/wiki/Computer-aided_manufacturing "Computer-aided manufacturing") systems require triangulated models. STL format is not the most memory- and computationally efficient method for transferring this data, but STL is often used to import the triangulated geometry into the [CAM](https://en.wikipedia.org/wiki/Computer-aided_manufacturing "Computer-aided manufacturing") system. The format is commonly available, so the CAM system can use it. In order to use the data, the CAM system may have to reconstruct the connectivity. As STL files do not save the physical dimension of a unit, a CAM system asks for it. Typical units are `mm` and `inch`.

STL can also be used for interchanging data between CAD/CAM systems and computational environments such as [Mathematica](https://en.wikipedia.org/wiki/Mathematica "Mathematica").

-   [3D Manufacturing Format](https://en.wikipedia.org/wiki/3D_Manufacturing_Format "3D Manufacturing Format") – Open source file format standard
-   [Additive Manufacturing File Format](https://en.wikipedia.org/wiki/Additive_Manufacturing_File_Format "Additive Manufacturing File Format") – Standard for describing objects for additive manufacturing
-   [PLY (file format)](https://en.wikipedia.org/wiki/PLY_(file_format) "PLY (file format)") – File format designed to store three-dimensional data from 3D scanners
-   [Voxel](https://en.wikipedia.org/wiki/Voxel "Voxel") – Element representing a value on a grid in three dimensional space
-   [Wavefront .obj file](https://en.wikipedia.org/wiki/Wavefront_.obj_file "Wavefront .obj file") – Geometry definition file format
-   [X3D](https://en.wikipedia.org/wiki/X3D "X3D") – XML-based file format for 3D computer graphics

1.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-1 "Jump up")** Noordvyk, Allan (6 March 2018). ["model/stl"](https://www.iana.org/assignments/media-types/model/stl). _iana.org_. [IANA](https://en.wikipedia.org/wiki/IANA "IANA"). [Archived](https://web.archive.org/web/20220216055141/https://www.iana.org/assignments/media-types/model/stl) from the original on 16 February 2022. Retrieved 30 May 2022.
2.  ^ [Jump up to: <sup><i><b>a</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-loc_2-0) [<sup><i><b>b</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-loc_2-1) [<sup><i><b>c</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-loc_2-2) [<sup><i><b>d</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-loc_2-3) [<sup><i><b>e</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-loc_2-4) ["STL (STereoLithography) File Format Family"](https://www.loc.gov/preservation/digital/formats/fdd/fdd000504.shtml). _Library of Congress_. [Archived](https://web.archive.org/web/20220529191656/https://www.loc.gov/preservation/digital/formats/fdd/fdd000504.shtml) from the original on 29 May 2022. Retrieved 30 May 2022.
3.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-3 "Jump up")** _StereoLithography Interface Specification_, 3D Systems, Inc., July 1988
4.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-4 "Jump up")** _StereoLithography Interface Specification_, 3D Systems, Inc., October 1989
5.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-5 "Jump up")** _SLC File Specification_, 3D Systems, Inc., 1994
6.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-6 "Jump up")** Grimm, Todd (2004). ["3. The Rapid Prototyping Process"](https://books.google.com/books?id=o2B7OmABPNUC&pg=PA55). _User's Guide to Rapid Prototyping_. [Society of Manufacturing Engineers](https://en.wikipedia.org/wiki/Society_of_Manufacturing_Engineers "Society of Manufacturing Engineers"). p. 55. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [0-87263-697-6](https://en.wikipedia.org/wiki/Special:BookSources/0-87263-697-6 "Special:BookSources/0-87263-697-6").
7.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-burkardt_7-0 "Jump up")** Burkardt, John (10 July 2014). ["STLA Files - ASCII stereolithography files"](https://people.math.sc.edu/Burkardt/data/stla/stla.html). [Archived](https://web.archive.org/web/20221004135829/https://people.math.sc.edu/Burkardt/data/stla/stla.html) from the original on 4 October 2022. Retrieved 30 May 2022.
8.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-fabbers_8-0 "Jump up")** ["The StL Format: Standard Data Format for Fabbers"](http://www.fabbers.com/tech/STL_Format). _fabbers.com — Historical resource on 3D printing_. [Archived](https://web.archive.org/web/20200917211707/http://www.fabbers.com/tech/STL_Format) from the original on 17 September 2020. Retrieved 30 May 2022.
9.  ^ [Jump up to: <sup><i><b>a</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-burns_9-0) [<sup><i><b>b</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-burns_9-1) [<sup><i><b>c</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-burns_9-2) Burns, Marshall (1993). "6.5". _Automated Fabrication: Improving Productivity in Manufacturing_. [Prentice Hall PTR](https://en.wikipedia.org/wiki/Prentice_Hall "Prentice Hall"). [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [9780131194625](https://en.wikipedia.org/wiki/Special:BookSources/9780131194625 "Special:BookSources/9780131194625"). [OCLC](https://en.wikipedia.org/wiki/OCLC_(identifier) "OCLC (identifier)") [634954895](https://search.worldcat.org/oclc/634954895).
10.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-10 "Jump up")** Chua, C. K.; Leong, K. F.; Lim, C. S. (2003), "Chapter 6, Rapid Prototyping Formats", _Rapid Prototyping: Principles and Applications_ (2nd ed.), [World Scientific Publishing Co.](https://en.wikipedia.org/wiki/World_Scientific "World Scientific"), p. 237, [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [981-238-117-1](https://en.wikipedia.org/wiki/Special:BookSources/981-238-117-1 "Special:BookSources/981-238-117-1"), The STL (STeroLithography) file, as the de facto standard, has been used in many, if not all, rapid prototyping systems.
11.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-All3DP_11-0 "Jump up")** ["STL File Format for 3D Printing - Explained in Simple Terms"](https://all3dp.com/what-is-stl-file-format-extension-3d-printing/). _All3DP_. 17 November 2016. [Archived](https://web.archive.org/web/20160922164726/https://all3dp.com/what-is-stl-file-format-extension-3d-printing/) from the original on 22 September 2016. Retrieved 5 May 2017.
12.  ^ [Jump up to: <sup><i><b>a</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-stl2_12-0) [<sup><i><b>b</b></i></sup>](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-stl2_12-1) ["STL 2.0 May Replace Old, Limited File Format"](http://www.rapidtoday.com/stl-file-format.html). _RapidToday_. [Archived](https://web.archive.org/web/20111229212656/http://www.rapidtoday.com/stl-file-format.html) from the original on 29 December 2011. Retrieved 5 May 2017.
13.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-13 "Jump up")** Hiller, Jonathan D.; Lipson, Hod (2009). [_STL 2.0: A Proposal for a Universal Multi-Material Additive Manufacturing File Format_](https://web.archive.org/web/20200611234339/https://sffsymposium.engr.utexas.edu/Manuscripts/2009/2009-23-Hiller.pdf) (PDF). Solid Freeform Fabrication Symposium (SFF'09). Austin, Texas, USA: Cornell University. Archived from [the original](https://sffsymposium.engr.utexas.edu/Manuscripts/2009/2009-23-Hiller.pdf) (PDF) on 11 June 2020. Retrieved 5 May 2017.
14.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-14 "Jump up")** Bourke, Paul (October 1999). ["STL format"](http://paulbourke.net/dataformats/stl/). [Archived](https://web.archive.org/web/20220716085920/http://paulbourke.net/dataformats/stl/) from the original on 16 July 2022. Retrieved 29 May 2022.
15.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-15 "Jump up")** ["STL (STereoLithography) File Format, ASCII"](https://www.loc.gov/preservation/digital/formats/fdd/fdd000506.shtml). _Library of Congress_. [Archived](https://web.archive.org/web/20220529191653/https://www.loc.gov/preservation/digital/formats/fdd/fdd000506.shtml) from the original on 29 May 2022. Retrieved 30 May 2022.
16.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-16 "Jump up")** Peddie, Jon (2013). _The History of Visual Magic in Computers: How Beautiful Images are Made in CAD, 3D, VR and AR_. London, England: Springer. pp. 54–57\. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [9781447149323](https://en.wikipedia.org/wiki/Special:BookSources/9781447149323 "Special:BookSources/9781447149323"). [OCLC](https://en.wikipedia.org/wiki/OCLC_(identifier) "OCLC (identifier)") [849634980](https://search.worldcat.org/oclc/849634980).
17.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-17 "Jump up")** ["What are NURBS?"](https://www.rhino3d.com/features/nurbs/). _www.rhino3d.com_. [Archived](https://web.archive.org/web/20210625180928/https://www.rhino3d.com/features/nurbs/) from the original on 25 June 2021. Retrieved 25 June 2021.
18.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-18 "Jump up")** ["Structure — Blender Manual"](https://docs.blender.org/manual/en/latest/modeling/surfaces/structure.html). _docs.blender.org_. [Archived](https://web.archive.org/web/20210625180929/https://docs.blender.org/manual/en/latest/modeling/surfaces/structure.html) from the original on 25 June 2021. Retrieved 25 June 2021.
19.  **[^](https://en.wikipedia.org/wiki/STL_(file_format)#cite_ref-19 "Jump up")** Barnatt, Christopher (2013). _3D Printing: The Next Industrial Revolution_. Nottingham, England: ExplainingTheFuture.com. pp. 26–71\. [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier) "ISBN (identifier)") [9781484181768](https://en.wikipedia.org/wiki/Special:BookSources/9781484181768 "Special:BookSources/9781484181768"). [OCLC](https://en.wikipedia.org/wiki/OCLC_(identifier) "OCLC (identifier)") [854672031](https://search.worldcat.org/oclc/854672031).

-   [The STL Format](http://www.fabbers.com/tech/STL_Format)
-   [ASCII stereolithography files](https://people.math.sc.edu/Burkardt/data/stla/stla.html)
