import argparse
import difflib
import os
import sys

import yaml

from . import CONFIG, info_print
from . import __version__

from .cleaner import clean_api_docs
from .loader import file_mappings, mapping_tostr
from .parsing import Parser
from .writer import write


def write_config_file():
    cwd = os.getcwd()

    conf = os.path.join(cwd, ".reslate-config.yaml")
    if os.path.isfile(conf):
        os.remove(conf)

    root_name = os.path.normpath(cwd).split(os.sep)[-1].split("_")[0]
    dirs_in_cwd = list(filter(lambda x: os.path.isdir(x), os.listdir(cwd)))

    closest_to_rootname = difflib.get_close_matches(root_name, dirs_in_cwd, n=1)
    if not closest_to_rootname:
        info_print(
            "WARNING: Unable to determine package_source_path. Please set this "
            "field manually in .reslate-config.yaml",
            True,
        )
        relative_source_path = ""
    else:
        relative_source_path = closest_to_rootname[0]

    closest_to_docs = difflib.get_close_matches("docs", dirs_in_cwd, n=1)
    if not closest_to_rootname:
        info_print(
            "WARNING: Unable to determine docs_source_path. Please set this "
            "field manually in .reslate-config.yaml",
            True,
        )
        relative_docs_src_path = ""
    else:
        relative_docs_path = closest_to_docs[0]

        docs_path = os.path.join(cwd, relative_docs_path)

        dirs_in_docs = list(
            filter(
                lambda x: os.path.isdir(os.path.abspath(os.path.join(docs_path, x))),
                os.listdir(docs_path),
            )
        )
        if "source" in dirs_in_docs:
            relative_docs_src_path = os.path.join(relative_docs_path, "source")
        elif "src" in dirs_in_docs:
            relative_docs_src_path = os.path.join(relative_docs_path, "src")
        else:
            relative_docs_src_path = relative_docs_path

    contents = r"""
# path to package source code relative to package root
package_source_path: %s

# path to package documentation source relative to package root
docs_source_path: %s

# files and patterns to exclude from documenting
exclude:
    files: ['^_', '^\.', 'version', 'test']
    subpkgs: ['^_', '^\.', 'version', 'test']

    classes: []
    enums: []
    dataclasses: []
    methods: []
    functions: []
    """ % (
        relative_source_path,
        relative_docs_src_path,
    )

    with open(conf, "w") as f:
        f.write(contents.strip() + "\n")

    info_print(f"Configuration file: {conf} written successfully.", True)


def find_config_file():
    directory = os.getcwd()

    conf_file = os.path.join(directory, ".reslate-config.yaml")

    while not os.path.isfile(conf_file) and directory:
        directory, _ = os.path.split(directory)
        conf_file = os.path.join(directory, ".reslate-config.yaml")

    if not directory:
        info_print("ERROR: Unable to find a .reslate-config.yaml file!", True)
        return None, None

    with open(conf_file, "r") as f:
        try:
            return yaml.safe_load(f), directory
        except yaml.YAMLError as ex:
            info_print(
                f"ERROR: Unable to load .reslate-config.yaml file, the "
                f"following yaml load error occurred:\n    {str(ex)}",
                True,
            )
            return None, directory


def _make_parser():
    parser = argparse.ArgumentParser(
        description="Generate and update API documentation."
    )

    parser.add_argument(
        "sources",
        nargs="*",
        help="Source files of package to generate / update API "
        "documentation pages from.",
    )

    parser.add_argument(
        "--init",
        dest="initialise",
        action="store_true",
        help="Initialise reslate for the current working directory. Note that "
        "the current working directory should be the root directory of your "
        "local copy of your package repository.",
        default=False,
    )
    parser.add_argument(
        "--clean", dest="clean", action="store_true", default=False,
    )

    parser.add_argument(
        "-V",
        "--version",
        help="Current version of reslate.",
        action="version",
        version="reslate v%s" % __version__,
    )
    parser.add_argument("-v", dest="verbose", action="store_true", default=False)

    return parser


def main():
    parser = _make_parser()

    # parse the args provided into a Namespace
    args = parser.parse_args()

    info_print(f"Running reslate v{__version__}", args.verbose)

    if args.initialise:
        info_print("Attempting to write .reslate-config.yaml file", True)
        write_config_file()
        info_print("Initialisation done, exiting.", True)
        return 0

    config, proj_root = find_config_file()
    if config is None:
        return -1

    pkg_src_path = config.get("package_source_path", "")
    if not pkg_src_path:
        info_print(
            "ERROR: package_source_path entry in loaded "
            ".reslate-config.yaml file is empty!",
            args.verbose,
        )
        return -1

    CONFIG.source = os.path.join(proj_root, os.path.normpath(pkg_src_path))
    info_print(f"Using package source path: {CONFIG.source}", args.verbose)
    info_print(f"Determined package name: {CONFIG.package_name}", args.verbose)

    docs_src_path = config.get("docs_source_path", "")
    if not docs_src_path:
        info_print(
            "ERROR: docs_source_path entry in loaded "
            ".reslate-config.yaml file is empty!",
            args.verbose,
        )
        return -1

    CONFIG.docs = os.path.join(proj_root, os.path.normpath(docs_src_path))
    info_print(f"Using docs source path: {CONFIG.docs}", args.verbose)

    if args.clean:
        clean_api_docs()

    exclude = config.get("exclude", {})
    CONFIG.exclude_files = exclude.get("files", [])
    CONFIG.exclude_pkgs = exclude.get("subpkgs", [])
    CONFIG.exclude_classes = exclude.get("classes", [])
    CONFIG.exclude_enums = exclude.get("enums", [])
    CONFIG.exclude_dataclasses = exclude.get("dataclasses", [])
    CONFIG.exclude_methods = exclude.get("methods", [])
    CONFIG.exclude_functions = exclude.get("functions", [])

    sources = []
    for src in args.sources:
        src = os.path.abspath(src)
        if os.path.isfile(src) and (src.endswith(".py") or src.endswith(".pyx")):
            sources.append(src)
        elif os.path.isdir(src):
            for root, _, files in os.walk(src):
                for f in files:
                    if f.endswith(".py") or f.endswith(".pyx"):
                        af = os.path.abspath(os.path.join(root, f))
                        sources.append(af)
        else:
            info_print(
                f"WARNING: Ignoring file or directory: {src} as it does not exist ",
                True,
            )

    if not sources:
        info_print("No source files given, exiting.", args.verbose)
        return 0

    subpkg_doc_files, submod_doc_files = file_mappings(sources)

    if args.verbose:
        info_print(
            f"Sub-package source -> doc file mappings:\n"
            f"{mapping_tostr(subpkg_doc_files)}\n",
            args.verbose,
        )
        info_print(
            f"Sub-module source -> doc file mappings:\n"
            f"{mapping_tostr(submod_doc_files)}\n",
            args.verbose,
        )

    map_sfi_to_docfile = {}
    for src, docfile in submod_doc_files.items():
        p = Parser(src)
        map_sfi_to_docfile[p.parse()] = docfile

    write(subpkg_doc_files, map_sfi_to_docfile)

    info_print(
        "API documentation files (mapped above) written successfully!", args.verbose
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
