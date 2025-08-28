DWARF Explorer
==============

A cross-platform GUI utility for visualizing the DWARF
debugging information in executable files, built on top of [pyelftools](https://github.com/eliben/pyelftools) and [filebytes](https://github.com/sashs/filebytes). Runs on Windows, MacOS X, and Linux. Supports parsing the following file types for DWARF data:
 - ELF (Linux, Android)
 - Mach-O (MacOS X, iOS)
 - PE (Windows, Cygwin)
 - WASM (aka WebAssembly)
 - ar (.a files, Linux/Unix/MacOS X static libraries)

This project came from my desire to see and navigate the DWARF tree of compiled Android and iOS binaries. Seeing the DIEs is easy enough with utilities like `readelf` or `dwarfdump`. However, chasing inter-DIE references back and forth is not straightforward with those.

The utility might be of use for anyone who is building DWARF parsers for one or another reason, especially if their preferred parsing library is `pyelftools`.

Note that regular Windows executables (EXE/DLL files) are PE files but don't, as a rule, contain DWARF information. The Microsoft toolchains (Visual Studio and the like) produce debugging information in Microsoft's own format, Program Database (PDB). There are, though, a couple of toolchains that produce PE files with DWARF debug info in them - notably GCC under Cygwin. DWARF Explorer is compatible with those.

The pyelftools library that dwex is based on supports DWARF versions 2-5, and so does dwex. DWARFv5 support might be unstable. DWARF v1 is supported experimentally, in ELF files only.

There is a known issue with incorrect parsing of DWARF in .o files and static libraries that contain them. See [eliben/pyelftools#564](https://github.com/eliben/pyelftools/issues/564).

Requirements and Dependencies
------------
 - Python 3.6.1+
 - PyQt6
 - filebytes 0.10.1+
 - pyelftools 0.30+

Installation
-------------

If necessary, install [the latest Python](https://www.python.org/downloads/) in the way that's appropriate for your OS. Run `pip install dwex` from the command line, under `sudo` or elevated command line if necessary.

On Windows, if `pip` and/or Python is not in PATH, use `c:\Python39\python -m pip install dwex`, substituting your own path to Python 3.

Alternatively, get the dwex source tree from Github, and run `python setup.py install` in the root folder of the package. In this scenario, you'd have to install the dependencies separately - with `pip install pyqt6 filebytes pyelftools`.

On Linux, sometimes the `python` command defaults to Python 2 while Python 3 is installed side by side. In this case, use `python3` and `pip3`, respectively. Use `python -V` to check.

Once you install it, there will be a `dwex` command. On Windows, there will be a `dwex.exe` in the `Scripts` folder under the Python folder, and also a start menu item "DWARF Explorer". On Linux, there
will be a "DWARF Explorer" in the app menu (tested under GNOME). On MacOS X, there will be "DWARF Explorer" in the Applications
folder, or in the user's Applications folder if the systemwide one is off limits.

In January 2022, the utility was migrated from PyQt5 to PyQt6, and the major version was bumped to 2. That cut off support for Python 3.5. The 1.x version that is compatible with Python 3.5 is still out in the repository, and pip should resolve it. 
If it does not, install by running `pip install "dwex<2"`.

Usage
-----

Click Open in the File menu, choose your executable, and eyeball the DWARF tree. Alternatively, drag and drop an executable onto the main window. You can open by dropping a dSYM bundle folder, too.

On the most basic level, the debug information in a compiled file is an array of *compilation units* (CUs). Each CU contains a tree of data items called *Debugging Information Entries* (DIEs). Each DIE has a title called *tag*, and contains a name-value dictionary called *attributes*. Each CU has exactly one root DIE, and the rest of the DIEs are in its subtree.

The UI of DWARF Explorer was meant for eyeballing that data structure:

![image](https://github.com/user-attachments/assets/2c2f426a-be59-437d-98bb-1520231641f5)

The left hand tree displays the DIEs, with CU root DIEs on the top level. Expand the tree and click on DIEs to see their attributes. DIE attributes that have a substructure or point at larger data structures are clickable.

DIEs generally correspond to source level entities in the program - variables, functions, classes, members, methods, etc. The DIE tag tells you which one is it. The exact way the compiler builds a DIE tree to describe the program varies between source languages, compiler versions, target platforms and architectures. The official home of the DWARF spec is at [dwarfstd.org](http://dwarfstd.org/), but there's considerable leeway for implementations to improvise upon. On top of that, the DWARF spec contains explicit extension points for compiler vendors to tap into.

DIE attribute values are relatively small scalars - integers, strings, sometimes short byte arrays. However, they sometimes refer at larger data structures. Physically, it's an integer, but logically, it's a pointer to some data elsewhere. Also, DIE attribute values may contain references to other DIEs - for example, a DIE for a variable would contain a reference to a DIE that describes its datatype. DIE attributes that contain references to other DIEs are rendered in blue; the link can be followed by a double-click or a Ctrl+Enter. To come back to the original DIE, use Navigate/Back, the Back mouse button, or an appropriate keyboard shortcut (Alt-Left on Windows and Linux, Ctrl-[ on Mac).

In DWARF, tag and attribute names are prefixed with `DW_TAG_` and `DW_AT_`, respectively. DWARF Explorer elides those by default to reduce visual clutter. Use `View/DWARF prefix` in the menu to bring them back.

Help DWEX get better
--------------------

Compilers and toolchains out there are a diverse bunch, compiled binaries even more so. **If you see DWARF Explorer crash, or misbehave, or complain about parsing errors - please don't hesitate to submit tickets at [github.com/sevaa/dwex/issues](https://github.com/sevaa/dwex/issues).** Ideally, attach the offending binary.


Disclaimer
----------

This project is unrelated to [ragundo/DwarfExplorer](https://github.com/ragundo/DwarfExplorer). That one deals with a different kind of dwarves. Although, interestingly enough, they also use the Qt library for their GUI.

Prior art
---------

There is also a GUI DWARF visualizer at [simark/dwarftree](https://github.com/simark/dwarftree). Also based on pyelftools,
with gtk based UI. It's been inactive since 2015. I didn't know about it when I started.

Pairs well with
---------------

For a free general purpose GUI ELF file visualizer, see [horsicq/XELFViewer](https://github.com/horsicq/XELFViewer). They also have a viewer for [Mach-O](https://github.com/horsicq/XMachOViewer) and [PE](https://github.com/horsicq/XPEViewer) binaries.
