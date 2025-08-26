from collections import OrderedDict
import re

from . import object_info as oi
from . import CONFIG

from .enums import MethodType


class SourceFileInfo(object):
    def __init__(self, src):
        self.src = src
        # TODO might be better to store all these as dicts
        #      of mapping - name : ObjectInfo
        self.classes = OrderedDict()
        self.enums = OrderedDict()
        self.dataclasses = OrderedDict()
        self.methods = {}  # {classname : {methname : MethodInfo}}
        self.functions = OrderedDict()

    def public(self, objtype=None, include_functions=False):
        if objtype is None:
            public = {}

            pclasses = self.public("classes")
            if pclasses:
                public["classes"] = pclasses

            penums = self.public("enums")
            if penums:
                public["enums"] = penums

            pdcs = self.public("dataclasses")
            if pdcs:
                public["dataclasses"] = pdcs

            if include_functions:
                pfuncs = self.public("functions")
                if pfuncs:
                    public["functions"] = pfuncs

            return public

        objects = getattr(self, objtype)

        return {k: v for k, v in objects.items() if v.is_public}

    def get_class_data(self, classname: str):
        if classname not in self.classes:
            raise ValueError("%s not in self.classes" % classname)

        all_methods = self.methods.get(classname, {})
        methods = {}
        properties = {}
        constructor = None
        for method_name, method_info in all_methods.items():
            if method_info.mtype == MethodType.METHOD and method_info.is_public:
                methods[method_name] = method_info
            elif method_info.mtype == MethodType.PROPERTY and method_info.is_public:
                properties[method_name] = method_info
            elif method_info.mtype == MethodType.CONSTRUCTOR:
                if constructor is not None:
                    raise Exception(
                        "BUG: class %s somehow has multiple constructors." % classname
                    )
                constructor = method_name, method_info

        return ClassData(classname, methods, constructor, properties)


class ClassData(object):
    def __init__(self, name, methods=None, constructor=None, properties=None):
        self.name = name
        self.methods = methods
        self.properties = properties
        self.constructor = constructor


def strip_base_args_whitespace(line):
    if "(" not in line or ")" not in line:
        return line.split(":")[0]

    start_paren_idx = line.index("(")
    end_paren_idx = line.index(")")

    bases = line[(1 + start_paren_idx) : end_paren_idx]
    reformed_bases = bases.replace(" ", "")

    return line.split("(")[0] + f"({reformed_bases})"


def is_class(line):
    return line.startswith("class") or line.startswith("cdef class")


def is_method(line, stripped):
    return (
        (stripped.startswith("def") or stripped.startswith("cpdef"))
        and "(" in line
        and len(line) - len(stripped) == 4
    )


def is_free_function(line, include_cdef=False):
    if line.startswith("def"):
        return True
    elif line.startswith("cpdef") or (line.startswith("cdef") and include_cdef):
        if "(" in line:
            return True
    return False


class Parser(object):
    def __init__(self, src):
        self.src = src
        self.sfi = SourceFileInfo(self.src)
        self.line = ""
        self.prev_line = ""

    def _parse_class(self, streampos):
        line = strip_base_args_whitespace(self.line)

        split = line.split(" ")
        if "cdef" in line:
            if len(split) > 3:
                split = split[:3]
            _, _, name_with_bases = split
        else:
            if len(split) > 2:
                split = split[:2]
            _, name_with_bases = split

        tmp = name_with_bases.split("(")
        if len(tmp) > 1:
            bases = tmp[1]
        else:
            bases = ""
        name = tmp[0].split(":")[0]

        if "Enum" in bases or "Flag" in bases:
            if all(re.search(p, name) is None for p in CONFIG.exclude_enums):
                self.sfi.enums[name] = oi.EnumInfo(name, self.src, streampos)
        elif "dataclass" in self.prev_line:
            if all(re.search(p, name) is None for p in CONFIG.exclude_dataclasses):
                self.sfi.dataclasses[name] = oi.DataClassInfo(name, self.src, streampos)
        else:
            if all(re.search(p, name) is None for p in CONFIG.exclude_classes):
                self.sfi.classes[name] = oi.ClassInfo(
                    name, self.src, streampos, "ABC" in bases
                )

    def _parse_free_function(self, streampos):
        # cases to consider:
        # 1) def foo():
        # 2) def foo(arg):
        # 3) def foo(arg1, arg2,):
        # 4) def foo(
        #       arg1, arg2,
        #    ):
        # 5) def foo(arg1,
        #       arg2,):
        # 6) def foo(arg1,
        #       arg2,
        #    ):
        #
        # 7) cpdef np.ndarray[double, ndim=2] compute_numeric_abcd(arg1, arg2)
        #
        # and all of the above with optional "arg : type" for typing support (along
        # with optional "-> type" after function declaration)
        # and (for Cython) all of the above with cpdef and optional type before foo

        # 4, 5 and 6 will require multi-line parsing so need to pass a handle
        # to the IO file stream to this function
        line = strip_base_args_whitespace(self.line)

        split = line.split(" ")
        if "cpdef" in line:
            if len(split) == 2:
                _, name_with_args = split
            else:
                if len(split) > 3:
                    # assume types can not have '(' characters
                    for item in split:
                        if "(" in item:
                            name_with_args = item
                else:
                    _, _type, name_with_args = split
        else:
            if len(split) > 2:
                split = split[:2]
            _, name_with_args = split

        tmp = name_with_args.split("(")
        name = tmp[0]

        if all(re.search(p, name) is None for p in CONFIG.exclude_functions):
            self.sfi.functions[name] = oi.FunctionInfo(name, self.src, streampos)

    def _parse_methods(self, src_handle):
        class_info_list = list(self.sfi.classes.values())
        for i, (classname, class_info) in enumerate(self.sfi.classes.items()):
            src_handle.seek(class_info.streampos)

            self.sfi.methods[classname] = OrderedDict()

            if class_info.streampos == class_info_list[-1].streampos:
                allclass = src_handle.read()
            else:
                allclass = src_handle.read(
                    class_info_list[i + 1].streampos - class_info.streampos
                )

            class_lines = allclass.splitlines()
            class_properties = set()
            for j, line in enumerate(class_lines):
                # also break on cdef, but don't normally include them in the docs
                # Broken outside of class now so leave
                if is_free_function(line, include_cdef=True) or line.startswith(
                    "class "
                ):
                    break

                stripped = line.strip()

                if is_method(line, stripped):
                    line = strip_base_args_whitespace(stripped)

                    line = line.split("(")[0]
                    split = line.split(" ")
                    if "cpdef" in line:
                        if len(split) == 2:
                            _, name_with_args = split
                        else:
                            if len(split) == 3:
                                _, _type, name_with_args = split
                            elif len(split) == 4:
                                _, _kw, _type, name_with_args = split
                            else:
                                raise RuntimeError(
                                    f"Encountered unparsable method signature: {line}"
                                )
                    else:
                        if len(split) > 2:
                            split = split[:2]
                        _, name_with_args = split

                    tmp = name_with_args.split("(")
                    method_name = tmp[0]
                    # Already got the actual property, so ignore
                    # the corresponding setter if it exists
                    if method_name in class_properties:
                        continue

                    if any(
                        re.search(p, method_name) is not None
                        for p in CONFIG.exclude_methods
                    ):
                        continue

                    is_property = class_lines[j - 1].lstrip().startswith("@property")
                    is_constructor = method_name == "__init__"

                    if is_property:
                        mtype = MethodType.PROPERTY
                        class_properties.add(method_name)
                    elif is_constructor:
                        mtype = MethodType.CONSTRUCTOR
                    else:
                        mtype = MethodType.METHOD

                    self.sfi.methods[classname][method_name] = oi.MethodInfo(
                        method_name, self.src, src_handle.tell(), mtype, class_info
                    )

    def parse(self):
        with open(self.src, encoding="utf8") as f:
            self.line = f.readline()

            in_docstrings = False
            while self.line:
                if not in_docstrings:
                    # Inside a module-level docstring...
                    if self.line.startswith('"""') or self.line.startswith('r"""'):
                        # ... check to see if it's multi-line
                        in_docstrings = self.line.count('"""') == 1
                    else:
                        if is_class(self.line):
                            self._parse_class(f.tell())
                        elif is_free_function(self.line):
                            self._parse_free_function(f.tell())
                else:  # Still inside a multi-line module-level docstring
                    # so check to see if it's ended
                    in_docstrings = not self.line.endswith('"""\n')

                self.prev_line = self.line
                self.line = f.readline()

            self._parse_methods(f)

        return self.sfi
