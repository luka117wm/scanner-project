---
created: 2026-04-19T05:35:02 (UTC +03:00)
tags: []
source: https://en.wikipedia.org/wiki/PLY_(file_format)
author: Contributors to Wikimedia projects
---

# PLY (file format) - Wikipedia

> ## Excerpt
> From Wikipedia, the free encyclopedia

---
From Wikipedia, the free encyclopedia

| Polygon File Format |
| --- |
| [Filename extension](https://en.wikipedia.org/wiki/Filename_extension "Filename extension") | 
.ply

 |
| [Internet media type](https://en.wikipedia.org/wiki/Media_type "Media type") | 

text/plain

 |
| [Type code](https://en.wikipedia.org/wiki/Resource_fork#Types "Resource fork") | [ASCII](https://en.wikipedia.org/wiki/ASCII "ASCII")/[Binary file](https://en.wikipedia.org/wiki/Binary_file "Binary file") |
| [Magic number](https://en.wikipedia.org/wiki/File_format#Magic_number "File format") | ply |
| Developed by | [Greg Turk](https://en.wikipedia.org/wiki/Greg_Turk "Greg Turk"), [Stanford University](https://en.wikipedia.org/wiki/Stanford_University "Stanford University") |
| Initial release | 1994<sup id="cite_ref-1"><a href="https://en.wikipedia.org/wiki/PLY_(file_format)#cite_note-1"><span>[</span>1<span>]</span></a></sup> |
| Type of format | 3D model format |

**PLY** is a computer file format known as the **Polygon File Format** or the **Stanford Triangle Format**. It was principally designed to store three-dimensional data from 3D scanners. The data storage format supports a relatively simple description of a single object as a list of nominally flat polygons. A variety of properties can be stored, including color and transparency, surface normals, texture coordinates and data confidence values. The format permits one to have different properties for the front and back of a polygon.

There are two versions of the [file format](https://en.wikipedia.org/wiki/File_format "File format"), one in [ASCII](https://en.wikipedia.org/wiki/ASCII "ASCII"), the other in [binary](https://en.wikipedia.org/wiki/Binary_file "Binary file").

A Ply file starts with the "header" attribute, which specifies the elements of a mesh and their types, followed by the list of elements itself. The elements are usually vertices and faces, but may include other entities such as edges, samples of range maps, and triangle strips.

The header of both ASCII and binary files is ASCII text. Only the numerical data that follows the header is different between the two versions. The header always starts with a "[magic number](https://en.wikipedia.org/wiki/Magic_number_(programming)#Magic_numbers_in_files "Magic number (programming)")", a line containing:

```
ply

```

which identifies the file as a PLY file. The second line indicates which variation of the PLY format this is. It should be one of the following:

```
format ascii 1.0
format binary_little_endian 1.0
format binary_big_endian 1.0

```

Future versions of the standard will change the revision number at the end - but 1.0 is the only version currently in use.

Comments may be placed in the header by using the word `comment` at the start of the line. Everything from there until the end of the line should then be ignored. e.g.:

```
comment This is a comment!

```

The `element` keyword introduces a description of how some particular data elements are stored and how many of them there are. Hence, in a file where there are 12 vertices, each represented as a floating point (X,Y,Z) triple, one would expect to see:

```
element vertex 12
property float x
property float y
property float z

```

Other `property` lines might indicate that colours or other data items are stored at each vertex and indicate the data type of that information. Regarding the data type, there are two variants depending on the source of the ply file. The type can be specified with one of `char uchar short ushort int uint float double`, or one of `int8 uint8 int16 uint16 int32 uint32 float32 float64`. For an object with ten polygonal faces, one might see:

```
element face 10
property list uchar int vertex_index

```

PLY implementations vary wildly in the property names. `vertex_indices` is more often used than `vertex_index`, for example in [Blender](https://en.wikipedia.org/wiki/Blender_(software) "Blender (software)") and [VTK](https://en.wikipedia.org/wiki/VTK "VTK"). The extended specification lists a "Core List (required)", "Second List (often used)" and "Third List (suggested extensions)" of property names.<sup id="cite_ref-2"><a href="https://en.wikipedia.org/wiki/PLY_(file_format)#cite_note-2"><span>[</span>2<span>]</span></a></sup>

The word `list` indicates that the data is a list of values, the first of which is the number of entries in the list (represented as a 'uchar' in this case). In this example each list entry is represented as an 'int'. At the end of the header, there must always be the line:

```
end_header

```

## ASCII or binary format

\[[edit](https://en.wikipedia.org/w/index.php?title=PLY_(file_format)&action=edit&section=2 "Edit section: ASCII or binary format")\]

In the ASCII version of the format, the vertices and faces are each described one to a line with the numbers separated by white space. In the binary version, the data is simply packed closely together at the `endianness` specified in the header and with the data types given in the `property` records. For the common `property list...` representation for polygons, the first number for that element is the number of vertices that the polygon has and the remaining numbers are the indices of those vertices in the preceding vertex list.

The PLY format was developed in the mid-90s by [Greg Turk](https://en.wikipedia.org/wiki/Greg_Turk "Greg Turk") and others in the Stanford graphics lab under the direction of Marc Levoy. Its design was inspired by the [Wavefront .obj format](https://en.wikipedia.org/wiki/Wavefront_.obj_file "Wavefront .obj file"). However, the Obj format lacked extensibility for arbitrary properties and groupings, so the `property` and `element` keywords were devised to generalize the notions of vertices, faces, associated data, and other groups.

The following is a full example of a PLY file which describes a cube mesh exported from [Blender](https://en.wikipedia.org/wiki/Blender_(software) "Blender (software)") version 4.0.2:

```
ply
format ascii 1.0
comment Created in Blender version 4.0.2
element vertex 14
property float x
property float y
property float z
property float nx
property float ny
property float nz
property float s
property float t
element face 6
property list uchar uint vertex_indices
end_header
1 1 1 0.5773503 0.5773503 0.5773503 0.625 0.5
-1 1 1 -0.5773503 0.5773503 0.5773503 0.875 0.5
-1 -1 1 -0.5773503 -0.5773503 0.5773503 0.875 0.75
1 -1 1 0.5773503 -0.5773503 0.5773503 0.625 0.75
1 -1 -1 0.5773503 -0.5773503 -0.5773503 0.375 0.75
-1 -1 1 -0.5773503 -0.5773503 0.5773503 0.625 1
-1 -1 -1 -0.5773503 -0.5773503 -0.5773503 0.375 1
-1 -1 -1 -0.5773503 -0.5773503 -0.5773503 0.375 0
-1 -1 1 -0.5773503 -0.5773503 0.5773503 0.625 0
-1 1 1 -0.5773503 0.5773503 0.5773503 0.625 0.25
-1 1 -1 -0.5773503 0.5773503 -0.5773503 0.375 0.25
-1 1 -1 -0.5773503 0.5773503 -0.5773503 0.125 0.5
1 1 -1 0.5773503 0.5773503 -0.5773503 0.375 0.5
-1 -1 -1 -0.5773503 -0.5773503 -0.5773503 0.125 0.75
4 0 1 2 3
4 4 3 5 6
4 7 8 9 10
4 11 12 4 13
4 12 0 3 4
4 10 9 0 12

```

The file starts with the header which defines a file in ASCII format. There are 14 vertices (6 faces \* 4 vertices - 10 vertices saved due to merging) and 6 faces in total. After the header, the vertex and face data is listed. The vertex list contains position (x,y,z), normals (nx,ny,nz) and texture coordinates (s,t) for each of the 14 vertices. The face list contains the vertex count (4) and the vertex indices for each of the 6 quadrilateral faces.

-   [STL (file format)](https://en.wikipedia.org/wiki/STL_(file_format) "STL (file format)"), another common file format for 3D printing
-   [Additive Manufacturing File Format](https://en.wikipedia.org/wiki/Additive_Manufacturing_File_Format "Additive Manufacturing File Format")
-   [Wavefront .obj file](https://en.wikipedia.org/wiki/Wavefront_.obj_file "Wavefront .obj file"), a 3D geometry definition file format with _.obj_ file extension
-   [glTF](https://en.wikipedia.org/wiki/GlTF "GlTF") - a [Khronos Group](https://en.wikipedia.org/wiki/Khronos_Group "Khronos Group") file format for 3D Scenes and models.
-   [Universal Scene Description](https://en.wikipedia.org/wiki/Universal_Scene_Description "Universal Scene Description") (USD).

## Open source software

\[[edit](https://en.wikipedia.org/w/index.php?title=PLY_(file_format)&action=edit&section=6 "Edit section: Open source software")\]

-   [CloudCompare](https://en.wikipedia.org/wiki/CloudCompare "CloudCompare") having a focus on [point clouds](https://en.wikipedia.org/wiki/Point_cloud "Point cloud") with some additional functions for meshes.
-   [GigaMesh Software Framework](https://en.wikipedia.org/wiki/GigaMesh_Software_Framework "GigaMesh Software Framework"): numerical computations on meshes in PLY (or OBJ).
-   [MeshLab](https://en.wikipedia.org/wiki/MeshLab "MeshLab"): generic application for visualizing, processing and converting three-dimensional meshes to or from the PLY file format.

1.  **[^](https://en.wikipedia.org/wiki/PLY_(file_format)#cite_ref-1 "Jump up")** Greg Turk. ["The PLY Polygon File Format"](https://web.archive.org/web/20161204152348/http://www.dcs.ed.ac.uk/teaching/cs4/www/graphics/Web/ply.html). Archived from [the original](http://www.dcs.ed.ac.uk/teaching/cs4/www/graphics/Web/ply.html) on 2016-12-04.
2.  **[^](https://en.wikipedia.org/wiki/PLY_(file_format)#cite_ref-2 "Jump up")** Greg Turk. ["The PLY Polygon File Format (extended)"](https://gamma.cs.unc.edu/POWERPLANT/papers/ply.pdf) (PDF).

-   [Library of Congress Format Description](https://www.loc.gov/preservation/digital/formats/fdd/fdd000501.shtml)
-   [PLY - Polygon File Format](https://paulbourke.net/dataformats/ply/)
-   [Some tools for working with PLY files (C source code)](https://www.cc.gatech.edu/projects/large_models/ply.html)
-   [rply - An Ansi C software library for reading and writing PLY files (MIT license)](https://w3.impa.br/~diego/software/rply/)
-   [libply - A C++ software library for reading and writing PLY files (GNU license)](https://web.archive.org/web/20151202190005/http://people.cs.kuleuven.be/~ares.lagae/libply/)
-   [plyodine - A C++23 library for reading and writing PLY files (BSD license)](https://github.com/BradleyMarie/plyodine/)
-   [Another C++ software library for reading and writing PLY files (GPL 3.0 license)](https://www-sop.inria.fr/members/Thijs.Van-Lankveld/prog/ply/doc/)
-   [A repository of 3D models stored in the PLY format](https://graphics.stanford.edu/data/3Dscanrep/)
