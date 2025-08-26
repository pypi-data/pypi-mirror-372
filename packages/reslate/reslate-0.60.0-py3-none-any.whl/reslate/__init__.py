import os
import re

try:
    from .version import version as __version__
except ImportError:
    __version__ = "?.?.?"


def info_print(msg, verbose_flag):
    if verbose_flag:
        print("[reslate] " + msg)


class Config(object):
    def __init__(self):
        self._psp = None
        self._pkgname = None
        self._dsp = None

        self._exclude_files = [], []
        self._exclude_pkgs = [], []
        self._exclude_classes = []
        self._exclude_enums = []
        self._exclude_dataclasses = []
        self._exclude_methods = []
        self._exclude_functions = []

    @property
    def source(self):
        return self._psp

    @source.setter
    def source(self, value):
        self._psp = value
        _, trailing = os.path.split(value)
        self._pkgname = trailing.strip()

    @property
    def docs(self):
        return self._dsp

    @docs.setter
    def docs(self, value):
        self._dsp = value

    @property
    def exclude_files(self):
        return self._exclude_files

    @exclude_files.setter
    def exclude_files(self, value):
        files = []
        patterns = []

        for val in value:
            if val.endswith(".py") or val.endswith(".pyx"):
                files.append(val)
            else:
                patterns.append(re.compile("%s" % val))

        self._exclude_files = files, patterns

    @property
    def exclude_pkgs(self):
        return self._exclude_pkgs

    @exclude_pkgs.setter
    def exclude_pkgs(self, value):
        pkgs = []
        patterns = []

        for val in value:
            patterns.append(re.compile("%s" % val))

        self._exclude_pkgs = pkgs, patterns

    @property
    def exclude_classes(self):
        return self._exclude_classes

    @exclude_classes.setter
    def exclude_classes(self, value):
        self._exclude_classes = value

    @property
    def exclude_enums(self):
        return self._exclude_enums

    @exclude_enums.setter
    def exclude_enums(self, value):
        self._exclude_enums = value

    @property
    def exclude_dataclasses(self):
        return self._exclude_dataclasses

    @exclude_dataclasses.setter
    def exclude_dataclasses(self, value):
        self._exclude_dataclasses = value

    @property
    def exclude_methods(self):
        return self._exclude_methods

    @exclude_methods.setter
    def exclude_methods(self, value):
        m = []
        for val in value:
            owner = None
            if "." in val:
                owner, val = val.split(".")

            m.append((val, owner))

        self._exclude_methods = m

    @property
    def exclude_functions(self):
        return self._exclude_functions

    @exclude_functions.setter
    def exclude_functions(self, value):
        self._exclude_functions = value

    @property
    def package_name(self):
        return self._pkgname


CONFIG = Config()
