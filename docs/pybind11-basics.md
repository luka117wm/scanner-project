---
created: 2026-04-19T05:26:23 (UTC +03:00)
tags: []
source: https://pybind11.readthedocs.io/en/stable/basics.html
author: 
---

# First steps - pybind11 documentation

> ## Excerpt
> Toggle table of contents sidebar

---
Toggle table of contents sidebar

This sections demonstrates the basic features of pybind11. Before getting started, make sure that development environment is set up to compile the included set of test cases.

## Compiling the test cases[#](https://pybind11.readthedocs.io/en/stable/basics.html#compiling-the-test-cases "Link to this heading")

### Linux/macOS[#](https://pybind11.readthedocs.io/en/stable/basics.html#linux-macos "Link to this heading")

On Linux you’ll need to install the **python-dev** or **python3-dev** packages as well as **cmake**. On macOS, the included python version works out of the box, but **cmake** must still be installed.

After installing the prerequisites, run

```
mkdir build
cd build
cmake ..
make check -j 4

```

The last line will both compile and run the tests.

### Windows[#](https://pybind11.readthedocs.io/en/stable/basics.html#windows "Link to this heading")

On Windows, only **Visual Studio 2017** and newer are supported.

Note

To use the C++17 in Visual Studio 2017 (MSVC 14.1), pybind11 requires the flag `/permissive-` to be passed to the compiler [to enforce standard conformance](https://docs.microsoft.com/en-us/cpp/build/reference/permissive-standards-conformance?view=vs-2017). When building with Visual Studio 2019, this is not strictly necessary, but still advised.

To compile and run the tests:

```
mkdir build
cd build
cmake ..
cmake --build . --config Release --target check

```

This will create a Visual Studio project, compile and run the target, all from the command line.

Note

If all tests fail, make sure that the Python binary and the testcases are compiled for the same processor type and bitness (i.e. either **i386** or **x86\_64**). You can specify **x86\_64** as the target architecture for the generated Visual Studio project using `cmake -A x64 ..`.

See also

Advanced users who are already familiar with Boost.Python may want to skip the tutorial and look at the test cases in the `tests` directory, which exercise all features of pybind11.

## Header and namespace conventions[#](https://pybind11.readthedocs.io/en/stable/basics.html#header-and-namespace-conventions "Link to this heading")

For brevity, all code examples assume that the following two lines are present:

```
#include <pybind11/pybind11.h>

namespace py = pybind11;

```

Note

`pybind11/pybind11.h` includes `Python.h`, as such it must be the first file included in any source file or header for [the same reasons as Python.h](https://docs.python.org/3/extending/extending.html#a-simple-example).

Some features may require additional headers, but those will be specified as needed.

## Creating bindings for a simple function[#](https://pybind11.readthedocs.io/en/stable/basics.html#creating-bindings-for-a-simple-function "Link to this heading")

Let’s start by creating Python bindings for an extremely simple function, which adds two numbers and returns their result:

```
int add(int i, int j) {
    return i + j;
}

```

For simplicity [\[1\]](https://pybind11.readthedocs.io/en/stable/basics.html#f1), we’ll put both this function and the binding code into a file named `example.cpp` with the following contents:

```
#include <pybind11/pybind11.h>

namespace py = pybind11;

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(example, m, py::mod_gil_not_used()) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
}

```

The `PYBIND11_MODULE()` macro creates a function that will be called when an `import` statement is issued from within Python. The module name (`example`) is given as the first macro argument (it should not be in quotes). The second argument (`m`) defines a variable of type `py::module_` which is the main interface for creating bindings. The method [`module_::def()`](https://pybind11.readthedocs.io/en/stable/reference.html#_CPPv4I0DpEN7module_3defER7module_PKcRR4FuncDpRK5Extra "module_::def") generates binding code that exposes the `add()` function to Python.

Note

Notice how little code was needed to expose our function to Python: all details regarding the function’s parameters and return value were automatically inferred using template metaprogramming. This overall approach and the used syntax are borrowed from Boost.Python, though the underlying implementation is very different.

pybind11 is a header-only library, hence it is not necessary to link against any special libraries and there are no intermediate (magic) translation steps. On Linux, the above example can be compiled using the following command:

```
$ c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) example.cpp -o example$(python3 -m pybind11 --extension-suffix)

```

Note

If you used [Include as a submodule](https://pybind11.readthedocs.io/en/stable/installing.html#include-as-a-submodule) to get the pybind11 source, then use `$(python3-config --includes) -Iextern/pybind11/include` instead of `$(python3 -m pybind11 --includes)` in the above compilation, as explained in [Building manually](https://pybind11.readthedocs.io/en/stable/compiling.html#building-manually).

For more details on the required compiler flags on Linux and macOS, see [Building manually](https://pybind11.readthedocs.io/en/stable/compiling.html#building-manually). For complete cross-platform compilation instructions, refer to the [Build systems](https://pybind11.readthedocs.io/en/stable/compiling.html#compiling) page.

The [python\_example](https://github.com/pybind/python_example) and [cmake\_example](https://github.com/pybind/cmake_example) repositories are also a good place to start. They are both complete project examples with cross-platform build systems. The only difference between the two is that [python\_example](https://github.com/pybind/python_example) uses Python’s `setuptools` to build the module, while [cmake\_example](https://github.com/pybind/cmake_example) uses CMake (which may be preferable for existing C++ projects).

Building the above C++ code will produce a binary module file that can be imported to Python. Assuming that the compiled module is located in the current directory, the following interactive Python session shows how to load and execute the example:

```
$ python
Python 3.9.10 (main, Jan 15 2022, 11:48:04)
[Clang 13.0.0 (clang-1300.0.29.3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import example
>>> example.add(1, 2)
3
>>>

```

## Keyword arguments[#](https://pybind11.readthedocs.io/en/stable/basics.html#keyword-arguments "Link to this heading")

With a simple code modification, it is possible to inform Python about the names of the arguments (“i” and “j” in this case).

```
m.def("add", &add, "A function which adds two numbers",
      py::arg("i"), py::arg("j"));

```

[`arg`](https://pybind11.readthedocs.io/en/stable/reference.html#_CPPv43arg "arg") is one of several special tag classes which can be used to pass metadata into [`module_::def()`](https://pybind11.readthedocs.io/en/stable/reference.html#_CPPv4I0DpEN7module_3defER7module_PKcRR4FuncDpRK5Extra "module_::def"). With this modified binding code, we can now call the function using keyword arguments, which is a more readable alternative particularly for functions taking many parameters:

```
>>> import example
>>> example.add(i=1, j=2)
3L

```

The keyword names also appear in the function signatures within the documentation.

```
>>> help(example)

....

FUNCTIONS
    add(...)
        Signature : (i: int, j: int) -> int

        A function which adds two numbers

```

A shorter notation for named arguments is also available:

```
// regular notation
m.def("add1", &add, py::arg("i"), py::arg("j"));
// shorthand
using namespace pybind11::literals;
m.def("add2", &add, "i"_a, "j"_a);

```

The `_a` suffix forms a C++11 literal which is equivalent to [`arg`](https://pybind11.readthedocs.io/en/stable/reference.html#_CPPv43arg "arg"). Note that the literal operator must first be made visible with the directive `using namespace pybind11::literals`. This does not bring in anything else from the `pybind11` namespace except for literals.

## Default arguments[#](https://pybind11.readthedocs.io/en/stable/basics.html#default-arguments "Link to this heading")

Suppose now that the function to be bound has default arguments, e.g.:

```
int add(int i = 1, int j = 2) {
    return i + j;
}

```

Unfortunately, pybind11 cannot automatically extract these parameters, since they are not part of the function’s type information. However, they are simple to specify using an extension of [`arg`](https://pybind11.readthedocs.io/en/stable/reference.html#_CPPv43arg "arg"):

```
m.def("add", &add, "A function which adds two numbers",
      py::arg("i") = 1, py::arg("j") = 2);

```

The default values also appear within the documentation.

```
>>> help(example)

....

FUNCTIONS
    add(...)
        Signature : (i: int = 1, j: int = 2) -> int

        A function which adds two numbers

```

The shorthand notation is also available for default arguments:

```
// regular notation
m.def("add1", &add, py::arg("i") = 1, py::arg("j") = 2);
// shorthand
m.def("add2", &add, "i"_a=1, "j"_a=2);

```

## Exporting variables[#](https://pybind11.readthedocs.io/en/stable/basics.html#exporting-variables "Link to this heading")

To expose a value from C++, use the `attr` function to register it in a module as shown below. Built-in types and general objects (more on that later) are automatically converted when assigned as attributes, and can be explicitly converted using the function `py::cast`.

```
PYBIND11_MODULE(example, m, py::mod_gil_not_used()) {
    m.attr("the_answer") = 42;
    py::object world = py::cast("World");
    m.attr("what") = world;
}

```

These are then accessible from Python:

```
>>> import example
>>> example.the_answer
42
>>> example.what
'World'

```

## Supported data types[#](https://pybind11.readthedocs.io/en/stable/basics.html#supported-data-types "Link to this heading")

A large number of data types are supported out of the box and can be used seamlessly as functions arguments, return values or with `py::cast` in general. For a full overview, see the [Type conversions](https://pybind11.readthedocs.io/en/stable/advanced/cast/index.html) section.
