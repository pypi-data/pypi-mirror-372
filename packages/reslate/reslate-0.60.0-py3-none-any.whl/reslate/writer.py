import os
import re

from . import templates
from . import CONFIG

from .loader import is_matching_file, is_matching_dir
from .parsing import SourceFileInfo


def write(subpkg_doc_files: dict, submod_doc_files: dict):
    for subpkg_dir, subpkg_doc_file in subpkg_doc_files.items():
        name = subpkg_doc_file.split(os.sep)[-1].replace(".rst", "")
        all_items = os.listdir(subpkg_dir)
        submodules = _filter_submodules(all_items, subpkg_dir)

        contents = templates.load.make_subpkg_overview(name, submodules)

        leading_dir, _ = os.path.split(subpkg_doc_file)
        os.makedirs(leading_dir, exist_ok=True)
        with open(subpkg_doc_file, "w+") as f:
            f.write(_format_writable(contents))

    for sfi, doc_file in submod_doc_files.items():
        _manipulate_doc_file(doc_file, sfi)


def _filter_submodules(items, subpkg_dir):
    submods = []

    for item in items:
        if item == "__pycache__":
            continue

        path = os.path.join(subpkg_dir, item)
        dd = os.path.normpath(path).split(os.sep)
        dd_rev = list(reversed(dd))
        pkg_idx = dd_rev.index(CONFIG.package_name)
        subpkg_unfolded = list(reversed(dd_rev[: (pkg_idx + 1)]))
        # if CONFIG.package_name in dd[(pkg_idx + 1) :]:
        #    pkg_idx += dd[(pkg_idx + 1) :].index(CONFIG.package_name)
        # subpkg_unfolded = dd[pkg_idx:]

        if os.path.isdir(path) and is_matching_dir(item):
            sub_items = os.listdir(path)
            if "__init__.py" in sub_items:
                submods.append(".".join(subpkg_unfolded))
        else:
            if is_matching_file(item):
                if subpkg_unfolded[-1].endswith(".py"):
                    subpkg_unfolded[-1] = subpkg_unfolded[-1].replace(".py", "")
                elif subpkg_unfolded[-1].endswith(".pyx"):
                    subpkg_unfolded[-1] = subpkg_unfolded[-1].replace(".pyx", "")

                submods.append(".".join(subpkg_unfolded))

    submods.sort()
    return submods


def _format_writable(contents: str):
    contents = contents.strip()
    return re.sub(r"\n\s*\n", "\n\n", contents) + "\n"


def _manipulate_doc_file(doc_file: str, sfi: SourceFileInfo):
    # recursively make all directories up to doc_file if they don't exist already
    os.makedirs(os.path.dirname(doc_file), exist_ok=True)

    public_objs = sfi.public()
    if not public_objs and not sfi.public("functions"):
        _, fname = os.path.split(doc_file)
        name = fname.replace(".rst", "")
        contents = templates.load.make_simplemod_header(name, name)
        with open(doc_file, "w+") as f:
            f.write(_format_writable(contents))
    else:
        _multiobj_handler(doc_file, sfi, public_objs)


def _multiobj_handler(doc_file: str, sfi: SourceFileInfo, objs: dict):
    leading_dir, fname = os.path.split(doc_file)
    new_dirname = fname.split(".")[-2]

    # Write the module level doc file first
    name = fname.replace(".rst", "")
    classes = list(objs.get("classes", {}).keys())
    dataclasses = list(objs.get("dataclasses", {}).keys())
    enums = list(objs.get("enums", {}).keys())
    functions = list(sfi.public("functions").keys())

    contents = templates.load.make_multiclass_header(
        name, name, new_dirname, classes, dataclasses, enums, functions,
    )
    with open(doc_file, "w+") as f:
        f.write(_format_writable(contents))

    # Now write all the sub doc files from all the objects
    # that exist within this module - creating a directory
    # with module name if it doesn't already exist
    full_new_dirname = os.path.join(leading_dir, new_dirname)
    if not os.path.isdir(full_new_dirname):
        os.mkdir(full_new_dirname)

    for obj_type, objects in objs.items():
        for obj in objects:  # NOTE: obj is the object name
            new_fname = ".".join(fname.split(".")[:-1]) + (".%s.rst" % obj)
            fpath = os.path.join(leading_dir, os.path.join(new_dirname, new_fname))

            name = new_fname.replace(".rst", "")
            mod_name = fname.replace(".rst", "")

            if obj_type == "classes":
                cd = sfi.get_class_data(obj)

                constructor = None if cd.constructor is None else cd.constructor[0]
                properties = list(cd.properties.keys())
                methods = list(cd.methods.keys())
            else:
                constructor = None
                properties = []
                methods = []

            contents = templates.load.make_singleobj_header(
                name, mod_name, obj, properties, methods, constructor,
            )

            with open(fpath, "w+") as f:
                f.write(_format_writable(contents))
