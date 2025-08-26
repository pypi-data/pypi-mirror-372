class ObjectInfo(object):
    def __init__(self, name, file, streampos):
        self.__name = name
        self.__file = file
        self.__streampos = streampos

        if name.startswith("__"):
            self.__access = "private"
        elif name.startswith("_"):
            self.__access = "protected"
        else:
            self.__access = "public"

    @property
    def name(self):
        return self.__name

    @property
    def is_private(self):
        return self.__access == "private"

    @property
    def is_protected(self):
        return self.__access == "protected"

    @property
    def is_public(self):
        return self.__access == "public"

    @property
    def owning_file(self):
        return self.__file

    @property
    def streampos(self):
        return self.__streampos


class ClassInfo(ObjectInfo):
    def __init__(self, name, file, streampos, abstract):
        super().__init__(name, file, streampos)
        self.__abstract = abstract

    @property
    def is_abstract(self):
        return self.__abstract


class EnumInfo(ObjectInfo):
    def __init__(self, name, file, streampos):
        super().__init__(name, file, streampos)


class DataClassInfo(ObjectInfo):
    def __init__(self, name, file, streampos):
        super().__init__(name, file, streampos)


class MethodInfo(ObjectInfo):
    def __init__(self, name, file, streampos, mtype, owner):
        super().__init__(name, file, streampos)
        self.__mtype = mtype
        self.__owner = owner

    @property
    def mtype(self):
        return self.__mtype

    @property
    def owner(self):
        return self.__owner


class FunctionInfo(ObjectInfo):
    def __init__(self, name, file, streampos):
        super().__init__(name, file, streampos)
