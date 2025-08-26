import inspect
import os

TEMPLATES_DIR = os.path.join(
    os.path.dirname(
        os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    ),
    "templates",
)

_VALID_MATCHES = list(filter(lambda x: x.endswith(".rst"), os.listdir(TEMPLATES_DIR)))


def load(name):
    if not name.endswith(".rst"):
        name += ".rst"

    if name not in _VALID_MATCHES:
        raise ValueError("Unrecognised template: %s" % name)

    with open(os.path.join(TEMPLATES_DIR, name)) as f:
        contents = f.read()

    return contents


def _indented_object_block(objects):
    block = "\n    ".join(sorted(objects))
    return block


def _header_break(name):
    return "".join(["=" for _ in range(len("``" + name + "``"))])


def make_subpkg_overview(name, submodules):
    header_break = _header_break(name)
    if submodules:
        split = name.split(".")
        if len(split) == 1:
            dirname = None
        else:
            dirname = split[-1]

        submodules_summaries = make_submodule_summaries(submodules, dirname,)
    else:
        submodules_summaries = ""

    return load("subpkg_overview").format(
        header_break=header_break, name=name, submodules=submodules_summaries
    )


def make_submodule_summaries(submodules, dirname=None):
    submod_block = _indented_object_block(submodules)
    if dirname is not None:
        toctree = ":toctree: {}/".format(dirname)
    else:
        toctree = ":toctree: ."

    return load("submodules_summaries").format(toctree=toctree, submodules=submod_block)


def make_classes_overview(dirname, classes):
    classes_block = _indented_object_block(classes)
    return load("classes_overview").format(dirname=dirname, classes=classes_block)


def make_dataclasses_overview(dirname, dcs):
    dataclasses_block = _indented_object_block(dcs)
    return load("dataclasses_overview").format(dirname=dirname, dcs=dataclasses_block)


def make_enums_overview(dirname, enums):
    enums_block = _indented_object_block(enums)
    return load("enums_overview").format(dirname=dirname, enums=enums_block)


def make_single_class_overview(name):
    return load("single_class_overview").format(name=name)


def make_functions_section(functions):
    functions_block = _indented_object_block(functions)
    return load("functions_section").format(functions=functions_block)


def make_properties_section(cls_name, properties):
    properties = ["%s.%s" % (cls_name, p) for p in properties]
    properties_block = _indented_object_block(properties)
    return load("properties_section").format(properties=properties_block)


def make_methods_section(cls_name, methods, constructor=None):
    methods = ["%s.%s" % (cls_name, m) for m in methods]
    methods_block = _indented_object_block(methods)

    if constructor is not None:
        constructor_block = "\n    %s" % constructor
    else:
        constructor_block = ""

    return load("methods_section").format(
        constructor=constructor_block, methods=methods_block
    )


def make_simplemod_header(name, modname):
    header_break = _header_break(name)

    return load("simplemod_header").format(
        header_break=header_break, name=name, module_name=modname,
    )


def make_singleobj_header(name, modname, obj_name, props, methods, constr):
    header_break = _header_break(name)

    obj_overview = make_single_class_overview(obj_name)

    if props:
        prop_section = make_properties_section(obj_name, props)
    else:
        prop_section = ""

    if methods:
        if constr is not None:
            constructor = "%s.%s" % (obj_name, constr)
        else:
            constructor = None

        meth_section = make_methods_section(obj_name, methods, constructor)
    else:
        meth_section = ""

    return load("singleclass_header").format(
        header_break=header_break,
        name=name,
        module_name=modname,
        overview=obj_overview,
        properties=prop_section,
        methods=meth_section,
    )


def make_multiclass_header(
    name: str,
    modname: str,
    subdir_name: str,
    classes: list,
    dataclasses: list,
    enums: list,
    functions: list,
):
    header_break = _header_break(name)

    if classes:
        classes_overview = make_classes_overview(subdir_name, classes)
    else:
        classes_overview = ""

    if dataclasses:
        dcs_overview = make_dataclasses_overview(subdir_name, dataclasses)
    else:
        dcs_overview = ""

    if enums:
        enums_overview = make_enums_overview(subdir_name, enums)
    else:
        enums_overview = ""

    if functions:
        functions_section = make_functions_section(functions)
    else:
        functions_section = ""

    return load("multiclass_header").format(
        header_break=header_break,
        name=name,
        module_name=modname,
        classes=classes_overview,
        dataclasses=dcs_overview,
        enums=enums_overview,
        functions=functions_section,
    )
