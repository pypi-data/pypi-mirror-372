# Copyright (c) 2020 Vemund Halmø Aarstrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import importlib.metadata as md

try:
    __version__: str = md.version("mjooln")
except md.PackageNotFoundError:
    __version__ = "N/A"

import base64
import datetime
import glob
import gzip
import hashlib
import json
import logging
import os
import re
import shutil
import signal
import socket
import string
import time
import uuid
import zipfile
from collections import namedtuple
from pathlib import Path as Path_
from pathlib import PurePath
from sys import platform
from threading import Event
from typing import Any, ClassVar, Dict, List, Optional, Protocol, Tuple, Union, runtime_checkable

import dateutil
import pytz
import simplejson
import yaml
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dateutil.parser import parse as dateparser

#######################################################################################
# Environment variables
#######################################################################################

#: Home folder. Default is '~/.mjooln'. Override by setting environment variable MJOOLN__HOME
HOME = os.getenv("MJOOLN__HOME", "~/.mjooln").replace("\\", "/")

# TODO: Add check to make sure word and class separator don't interfere with each other, and path separator
#: Default values. Override by adding MJOOLN__ first, and put in environment
#: variables
DEFAULT = {
    "PIXIE": "false",
    "MINIMUM_WORD_LENGTH": 1,
    "WORD_SEPARATOR": "__",
    "CLASS_SEPARATOR": "___",
    "COMPRESSED_EXTENSION": "gz",
    "ENCRYPTED_EXTENSION": "aes",
    "ZULU_TO_ISO": "true",
    "TRUNK__PATH": os.path.join(HOME, "trunk.yaml").replace("\\", "/"),
    "TRUNK__EXTENSION": "yaml",
    "TRUNK__AUTO_SCAN": "true",
    "TRUNK__AUTO_SCAN_FOLDERS": "",
}


def get_env(name) -> str:
    public_name = "MJOOLN__" + name
    return os.getenv(public_name, str(DEFAULT[name]))


#: When flag is set to 'true', the Pixie will slow down your code, but
#: in return be very picky about your mistakes
PIXIE: bool = get_env("PIXIE") == "true"

#: Minimum word length. Default is 1
MINIMUM_WORD_LENGTH: int = int(get_env("MINIMUM_WORD_LENGTH"))

#: Word separator. Default is double underscore
WORD_SEPARATOR: str = get_env("WORD_SEPARATOR")

#: Class separator. Default is triple underscore
CLASS_SEPARATOR: str = get_env("CLASS_SEPARATOR")

#: Compressed (reserved) extension. Default is '.gz'
COMPRESSED_EXTENSION: str = get_env("COMPRESSED_EXTENSION")

#: Encrypted (reserved) extension. Default is '.aes'
ENCRYPTED_EXTENSION: str = get_env("ENCRYPTED_EXTENSION")

#: Flags converting Zulu to iso string when creating doc
ZULU_TO_ISO: bool = get_env("ZULU_TO_ISO") == "true"


#######################################################################################
# Exceptions
#######################################################################################


class MjoolnException(Exception):
    """
    Parent for all module specific exceptions
    """

    pass


class PixieInPipeline(MjoolnException):
    """
    Raised by code mistakes if environment variable
    ``MJOOLN__PIXIE_IN_PIPELINE=true``
    """

    pass


class AngryElf(MjoolnException):
    """
    Raised when ``elf()`` is unable to figure out what you are trying to do.
    It usually does not take well to not being able to do magic
    """

    pass


class CryptError(MjoolnException):
    """
    Rased by :class:`.Crypt`, mainly when password or crypt_key is invalid
    """

    pass


class BadSeed(MjoolnException):
    """
    Raised by :class:`.Seed`
    """

    pass


class DicError(MjoolnException):
    """
    Raised by :class:`.Dic`
    """

    pass


class DocError(MjoolnException):
    """
    Raised by :class:`.Doc`
    """

    pass


class DocumentError(DocError):
    """
    Raised by :class:`.Document`
    """

    pass


class IdentityError(MjoolnException):
    """
    Raised by :class:`.Identity`
    """

    pass


class BadWord(MjoolnException):
    """
    Raised by :class:`.Word`
    """

    pass


class NotAnInteger(BadWord):
    """
    Raised by :class:`.Word` when trying to get an integer from a non-integer
    word
    """

    pass


class InvalidKey(MjoolnException):
    """
    Raised by :class:`.Key`
    """

    pass


class ZuluError(MjoolnException):
    """
    Raised by :class:`.Zulu`
    """

    pass


class AtomError(MjoolnException):
    """
    Raised by :class:`.Atom`
    """

    pass


class PathError(MjoolnException):
    """
    Raised by :class:`.Path`
    """

    pass


class FolderError(MjoolnException):
    """
    Raised by :class:`.Folder`
    """

    pass


class FileError(MjoolnException):
    """
    Raised by :class:`.File`
    """

    pass


class ArchiveError(MjoolnException):
    """
    Raised by :class:`.Archive`
    """

    pass


class StoreError(MjoolnException):
    """
    Raised by :class:`.Store`
    """

    pass


#######################################################################################
# Core
#######################################################################################


class Crypt:
    """Wrapper for best practice key generation and AES 128 encryption

    From `Fernet Docs <https://cryptography.io/en/latest/fernet/>`_:
    HMAC using SHA256 for authentication, and PKCS7 padding.
    Uses AES in CBC mode with a 128-bit key for encryption, and PKCS7 padding.
    """

    # TODO: Do QA on cryptographic strength

    @classmethod
    def generate_key(cls) -> bytes:
        """Generates URL-safe base64-encoded random key with length 44"""
        return Fernet.generate_key()

    @classmethod
    def salt(cls) -> bytes:
        """Generates URL-safe base64-encoded random string with length 24

        :return: bytes
        """

        # Used 18 instead of standard 16 since encode otherwise leaves
        # two trailing equal signs (==) in the resulting string
        return base64.urlsafe_b64encode(os.urandom(18))

    @classmethod
    def key_from_password(cls, salt: bytes, password: str) -> bytes:
        """Generates URL-safe base64-encoded random string with length 44

        :type salt: bytes
        :type password: str
        :return: bytes
        """

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @classmethod
    def encrypt(cls, data: bytes, key: bytes) -> bytes:
        """Encrypts input data with the given key

        :type data: bytes
        :type key: bytes
        :return: bytes
        """
        if key is None:
            raise CryptError("Encryption key missing, cannot encrypt")
        fernet = Fernet(key)
        return fernet.encrypt(data)

    @classmethod
    def decrypt(cls, data: bytes, key: bytes) -> bytes:
        """Decrypts input data with the given key

        :type data: bytes
        :type key: bytes
        :return: bytes
        """
        if key is None:
            raise CryptError("Encryption key missing, cannot encrypt")
        fernet = Fernet(key)
        try:
            return fernet.decrypt(data)
        except InvalidToken as it:
            raise CryptError(f"Invalid token. Probably due to " f"invalid password/key. Actual message: {it}")


class Glass:
    @classmethod
    def glass(cls, *args, **kwargs) -> Any:
        """
        If input is a class instance, return instance. If not, call
        constructor with same input arguments
        """
        if args and len(args) == 1 and not kwargs and isinstance(args[0], cls):
            return args[0]
        else:
            return cls(*args, **kwargs)


class Math:
    """Utility math methods"""

    @classmethod
    def human_size(cls, size_bytes: int) -> Tuple[float, str]:
        """Convert bytes to a human readable format

        :type size_bytes: int
        :return: Tuple of size as a float and unit as a string
        :rtype: (float, str)
        """
        # 2**10 = 1024
        power = 2**10
        n = 0
        size = float(size_bytes)
        power_labels = {0: "", 1: "k", 2: "M", 3: "G", 4: "T"}
        while size > power:
            size /= power
            n += 1
        return size, power_labels[n] + "B"

    @classmethod
    def bytes_to_human(cls, size_bytes: int, min_precision=5) -> str:
        """
        Convert size in bytes to human readable string

        :param size_bytes: Bytes
        :param min_precision: Minimum precision in number of digits
        :return:
        """
        value, unit = cls.human_size(size_bytes=size_bytes)
        len_int = len(str(int(value)))
        if len_int >= min_precision or unit == "B":
            len_dec = 0
        else:
            len_dec = min_precision - len_int
        return f"{value:.{len_dec}f} {unit}"


class Text:
    """String utility functions"""

    _CAMEL_TO_SNAKE = r"(?<!^)(?=[A-Z])"
    _SNAKE_TO_CAMEL = r"(.+?)_([a-z])"
    _RE_CAMEL_TO_SNAKE = re.compile(_CAMEL_TO_SNAKE)
    _RE_SNAKE_TO_CAMEL = re.compile(_SNAKE_TO_CAMEL)

    @classmethod
    def camel_to_snake(cls, camel: str) -> str:
        """
        Convert camel to snake::

            Text.camel_to_snake('ThisIsCamel')
                this_is_camel
        """
        return cls._RE_CAMEL_TO_SNAKE.sub("_", camel).lower()

    @classmethod
    def snake_to_camel(cls, snake: str) -> str:
        """
        Convert snake to camel::

            Text.snake_to_camel('this_is_snake')
                ThisIsSnake
        """
        # TODO: Implement regex instead
        return "".join(x[0].upper() + x[1:] for x in snake.split("_"))


@runtime_checkable
class Seed(Protocol):
    """
    Convenience methods for unique string representation of an object

    Object can be created with the method ``from_seed()``, but the method
    must be overridden in child class. ``find`` methods use the class variable
    ``REGEX``, which must also be overridden in child class

    If the seed has a fixed length, this can be specified in the class
    variable ``LENGTH``, and will speed up identification (or will it...)
    """

    #: Regex identifying seed must be overridden in child class
    REGEX: ClassVar[str]

    #: If seed has a fixed length, override in child class
    LENGTH: Optional[int] = None

    @classmethod
    def _search(cls, str_: str):
        if not cls.REGEX:
            raise BadSeed("REGEX must be overridden in child class")
        return re.compile(cls.REGEX).search(str_)

    @classmethod
    def _exact_match(cls, str_: str):
        if not cls.REGEX:
            raise BadSeed("_REGEX must be overridden in child class")
        _regex_exact = rf"^{cls.REGEX}$"
        return re.compile(_regex_exact).match(str_)

    @classmethod
    def verify_seed(cls, str_: str):
        """
        Check if string is seed

        :raise BadSeed: If string is not seed
        :param str_: Seed to verify
        """
        if not cls.is_seed(str_):
            raise BadSeed(f"Sting is not seed: {str_}")

    @classmethod
    def is_seed(cls, str_: str) -> bool:
        """
        Checks if input string is an exact match for seed

        :param str_: Input string
        :return: True if input string is seed, False if not
        """
        if cls.LENGTH and len(str_) != cls.LENGTH:
            return False
        return cls._exact_match(str_) is not None

    @classmethod
    def seed_in(cls, str_: str) -> bool:
        """Check if input string contains one or more seeds

        :param str_: String to check
        :type str_: str
        :return: True if input string contains one or more seeds, false if not
        """
        if cls._search(str_):
            return True
        else:
            return False

    @classmethod
    def find_seed(cls, str_: str) -> Any:
        """
        Looks for and returns exactly one object from text

        Uses ``from_seed()`` to instantiate object from seed and will fail if
        there are none or multiple seeds.
        Use find_all() to return a list of identities in text, including
        an empty list if there are none

        :raise BadSeed: If none or multiple seeds are found in string
        :param str_: String to search for seed
        :type str_: str
        :return: Seed object
        """
        res = re.findall(cls.REGEX, str_)
        if len(res) == 1:
            return cls.from_seed(res[0])
        elif not res:
            raise BadSeed(
                f"No {cls.__name__} found in this text: '{str_}'; "
                f"Consider using find_seeds(), which will "
                f"return empty list if none are found."
            )
        else:
            raise BadSeed(
                f"Found {len(res)} instances of {cls.__name__} in this "
                f"text: '{str_}'; "
                f"Use find_all() to return a list of all instances"
            )

    @classmethod
    def find_seeds(cls, str_: str) -> Any:
        """Finds and returns all seeds in text

        :type str_: str
        :return: List of objects
        """
        ids = re.findall(cls.REGEX, str_)
        return [cls.from_seed(x) for x in ids]

    @classmethod
    def from_seed(cls, str_: str):
        """
        Must be overridden in child class.

        Will create an object from seed

        :param str_: Seed
        :return: Instance of child class
        """
        raise BadSeed(f"Method from_seed() must be overridden " f"in child class '{cls.__name__}")

    def seed(self) -> str:
        """
        Get seed of current object.

        Default is ``str(self)``

        :return: :class:`Seed`
        """
        return str(self)


class Dic:
    """Enables child classes to mirror attributes and dictionaries

    Private variables start with underscore, and are ignored by default.

    .. note:: Meant for inheritance and not direct use, but can be initialized
        with a dictionary and will then serve as a struct, where keys can be
        accessed using dot notation

    Direct use example::

        dic = Dic(a=1, b=2, c='three')
        dic.to_dict()
            {'a': 1, 'b': 2, 'c': 'three'}
        dic.a
            1
        dic.b
            2
        dic.c
            'three'

        dic.c = 'four'
        dic.to_dict()
            {'a': 1, 'b': 2, 'c': 'four'}


    """

    _PRIVATE_STARTSWITH = "_"

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            if isinstance(args[0], dict):
                self.add(args[0])
            elif PIXIE:
                raise PixieInPipeline(
                    "Only allowed argument for constructor is " "a dict. Use kwargs, or inheritance for customization"
                )
        elif len(args) > 1 and PIXIE:
            raise PixieInPipeline(
                "Dic cannot be instantiated with multiple args, only " "kwargs. Use inheritance for customization"
            )
        self.add(kwargs)

    @classmethod
    def from_dict(cls, di: dict):
        """
        Create a new object from input dictionary
        """
        return cls(**di)

    def to_vars(self, ignore_private: bool = True) -> dict:
        di = vars(self).copy()
        if ignore_private:
            pop_keys = [x for x in di if x.startswith(self._PRIVATE_STARTSWITH)]
            for key in pop_keys:
                di.pop(key)

        return di

    def to_dict(self, ignore_private: bool = True, recursive: bool = False) -> dict:
        # TODO: Populate to_doc etc with recursive, same way as ignoreprivate
        """Return dictionary with a copy of attributes

        :param ignore_private: Ignore private attributes flag
        :return: dict
        """
        di = self.to_vars(ignore_private=ignore_private)
        if recursive:
            for key, item in di.items():
                if isinstance(item, Dic):
                    di[key] = item.to_vars(ignore_private=ignore_private)
        return di

    def keys(self, ignore_private=True) -> List[str]:
        dic = self.to_dict(ignore_private=ignore_private)
        return [str(x) for x in dic.keys()]

    def __repr__(self):
        di = self.to_vars()
        dicstr = []
        for key, item in di.items():
            dicstr.append(f"{key}={item.__repr__()}")
        dicstr_ = ", ".join(dicstr)
        return f"{type(self).__name__}({dicstr_})"

    def _add_item(self, key, item, ignore_private=True):
        # Add item and ignore private items if ignore_private is set to True
        if not ignore_private or not key.startswith(self._PRIVATE_STARTSWITH):
            self.__setattr__(key, item)

    def _add_dict(self, dic: dict, ignore_private: bool = True):
        for key, item in dic.items():
            self._add_item(key, item, ignore_private=ignore_private)

    def add(self, dic: dict, ignore_private: bool = True):
        """Add dictionary to class as attributes

        :param dic: Dictionary to add
        :param ignore_private: Ignore private attributes flag
        :return: None
        """
        self._add_dict(dic, ignore_private=ignore_private)

    # TODO: Consider always requiring equal
    def add_only_existing(self, dic, ignore_private=True):
        """Add dictionary keys and items as attributes if they already exist
        as attributes

        :param dic: Dictionary to add
        :param ignore_private: Ignore private attributes flag
        :return: None
        """
        dic_to_add = {}
        for key in dic:
            if hasattr(self, key):
                dic_to_add[key] = dic[key]
        self._add_dict(dic_to_add, ignore_private=ignore_private)

    # TODO: Consider decprecation
    def force_equal(self, dic, ignore_private=True):
        """Add all dictionary keys and items as attributes in object, and
        delete existing attributes that are not keys in the input dictionary

        :param dic: Dictionary to add
        :param ignore_private: Ignore private attributes flag
        :return: None
        """
        self._add_dict(dic, ignore_private=ignore_private)
        for key in self.to_dict(ignore_private=ignore_private):
            if key not in dic:
                self.__delattr__(key)

    def print(self, ignore_private=True, indent=4 * " ", width=80, flatten=False, separator=WORD_SEPARATOR):
        """
        Pretty print object attributes in terminal

        :param ignore_private: Ignore private variables flag
        :param indent: Spacing for sub dictionaries
        :param width: Target width of printout
        :param flatten: Print as joined keys
        :param separator: Key separator when flattening
        """
        text = f"--{indent}[[ {type(self).__name__} ]]{indent}"
        text += (width - len(text)) * "-"
        print(text)
        if not flatten:
            dic = self.to_dict(ignore_private=ignore_private)
        else:
            dic = self.to_flat(sep=separator)
        self._print(dic, level=0)
        print(width * "-")

    def _print(self, dic, level=0, indent=4 * " "):
        for key, item in dic.items():
            if isinstance(item, dict):
                print(level * indent + f"{key}: [dict]")
                self._print(item, level=level + 1)
            elif isinstance(item, Dic) and not isinstance(item, Seed):
                item = item.to_dict()
                print(level * indent + f"{key}: [{type(item).__name__}]")
                self._print(item, level=level + 1)
            else:
                print(level * indent + f"{key}: " f"[{type(item).__name__}] {item} ")

    def print_flat(self, ignore_private=True, separator=WORD_SEPARATOR):
        self.print(ignore_private=ignore_private, separator=separator, flatten=True)

    # TODO: Move to flag in to_dict etc., and unflatten in from_dict etc
    # TODO: Replace sep with Key sep.
    # TODO: Require var names not to have double underscores
    # TODO: Figure out how to handle __vars__, what is the difference with _vars

    def to_flat(self, sep=WORD_SEPARATOR, ignore_private=True):
        """
        Flatten dictionary to top elements only by combining keys of
         sub dictionaries with the given separator

        :param sep: Separator to use, default is double underscore (__)
        :type sep: str
        :param ignore_private: Flags whether to ignore private attributes,
            identified by starting with underscore
        :return: Flattened dictionary
        :rtype: dict
        """
        di = self.to_dict(ignore_private=ignore_private)
        return self.flatten(di, sep=sep)

    @classmethod
    def from_flat(cls, di_flat: dict, sep=WORD_SEPARATOR):
        return cls.from_dict(cls.unflatten(di_flat, sep=sep))

    @classmethod
    def _flatten(cls, di: dict, parent_key="", sep=WORD_SEPARATOR):
        items = []
        for key, item in di.items():
            if parent_key:
                new_key = parent_key + sep + key
            else:
                new_key = key
            if isinstance(item, dict):
                items.extend(cls._flatten(item, new_key, sep=sep).items())
            else:
                items.append((new_key, item))
        return dict(items)

    @classmethod
    def flatten(cls, di: dict, sep=WORD_SEPARATOR):
        """
        Flattens input dictionary with given separator
        :param di: Input dictionary
        :param sep: Separator (default is \'__\')
        :return: Flattened dictionary
        :rtype: dict
        """
        return cls._flatten(di, sep=sep)

    @classmethod
    def unflatten(cls, di_flat: dict, sep=WORD_SEPARATOR):
        """
        Unflattens input dictionary using the input separator to split into
        sub dictionaries
        :param di_flat: Input dictionary
        :param sep: Separator (default is \'__\')
        :return: Dictionary
        :rtype: dict
        """
        di: Dict[str, Any] = dict()
        for flat_key, item in di_flat.items():
            keys = flat_key.split(sep)
            di_tmp = di
            for key in keys[:-1]:
                if key not in di_tmp:
                    di_tmp[key] = dict()
                di_tmp = di_tmp[key]
            di_tmp[keys[-1]] = item
        return di


class JSON:
    """Dict to/from JSON string, with optional human readable"""

    @classmethod
    def dumps(cls, di, human=True, sort_keys=False, indent=4 * " "):
        """Convert from dict to JSON string

        :param di: Input dictionary
        :type di: dict
        :param human: Human readable flag
        :param sort_keys: Sort key flag (human readable only)
        :param indent: Indent to use (human readable only)
        :return: JSON string
        :rtype: str
        """
        if human:
            return simplejson.dumps(di, sort_keys=sort_keys, indent=indent)
        else:
            return json.dumps(di)

    @classmethod
    def loads(cls, json_string):
        """Parse JSON string to dictionary

        :param json_string: JSON string
        :type json_string: str
        :return: Dictionary
        :rtype: dict
        """
        return simplejson.loads(json_string)

    @classmethod
    def to_yaml(cls, json_string):
        di = cls.loads(json_string)
        return YAML.dumps(di)


class YAML:
    @classmethod
    def dumps(cls, di: dict):
        """
        Convert dictionary to YAML string

        :param di: Input dictionary
        :type di: dict
        :return: YAML string
        :rtype: str
        """
        return yaml.safe_dump(di)

    @classmethod
    def loads(cls, yaml_str):
        """
        Convert YAML string to dictionary

        :param yaml_str: Input YAML string
        :type yaml_str: str
        :return: Dictionary
        :rtype: dict
        """
        return yaml.safe_load(yaml_str)

    @classmethod
    def to_json(cls, yaml_str, human=False):
        di = cls.loads(yaml_str)
        return JSON.dumps(di, human=human)


# TODO: Add zulu/key/identity as builtin? Alternatively optional with environment variable
class Doc(Dic):
    """
    Enables child classes to mirror attributes, dictionaries, JSON and
    YAML

    .. note:: ``to_doc`` and ``from_doc`` are meant to be overridden in
        child class if attributes are not serializable. Both methods are
        used by JSON and YAML conversions
    """

    @classmethod
    def from_doc(cls, doc: dict):
        """
        Convert input dictionary to correct types and return object

        .. note:: Override in child class to handle custom types

        :param doc: Dictionary with serializable items only
        :return: New Doc object instantiated with input dictionary
        :rtype: Doc
        """
        return cls.from_dict(doc)

    @classmethod
    def from_json(cls, json_string: str):
        """
        Create :class:`Doc` from input JSON string
        :param json_string: JSON string
        :return: Doc
        """
        doc = JSON.loads(json_string=json_string)
        return cls.from_doc(doc)

    @classmethod
    def from_yaml(cls, yaml_string: str):
        """
        Create :class:`Doc` from input YAML string
        :param yaml_string: YAML string
        :return: Doc
        """
        doc = YAML.loads(yaml_string)
        return cls.from_doc(doc)

    def add_yaml(self, yaml_string: str, ignore_private=True):
        """
        Convert input YAML string to dictionary and add to current object

        :param yaml_string: YAML string
        :return: Doc
        """
        dic = YAML.loads(yaml_string)
        self.add(dic, ignore_private=ignore_private)

    def add_json(self, json_string: str, ignore_private=True):
        """
        Convert input JSON string to dictionary and add to current object

        :param json_string: JSON string
        :return: Doc
        """
        dic = JSON.loads(json_string)
        self.add(dic, ignore_private=ignore_private)

    def to_doc(self):
        """
        Converts class attributes to dictionary of serializable attributes

        ..note:: Override in child class to handle custom types

        :return: Dictionary of serialized objects
        """
        doc = self.to_dict(ignore_private=True)
        for key, item in doc.items():
            if ZULU_TO_ISO and isinstance(item, Zulu):
                doc[key] = item.iso()
            elif isinstance(item, Seed):
                doc[key] = item.seed()
            elif isinstance(item, Path):
                doc[key] = str(item)
        return doc

    def to_json(self, human: bool = False):
        """
        Convert object to JSON string
        :param human: Use human readable format
        :return: JSON string
        :rtype: str
        """
        doc = self.to_doc()
        return JSON.dumps(doc, human=human)

    def to_yaml(self):
        """
        Convert object to YAML string
        :return: YAML string
        :rtype: str
        """
        doc = self.to_doc()
        return YAML.dumps(doc)


class Tic:
    """
    Time counter

    Example::

        tic = Tic()

        (wait a bit)

        tic.toc()
            2.5361578464508057

        tic.toc('Elapsed time')
            'Elapsed time: 17.219 seconds'
    """

    def __init__(self):
        self.start_time = time.time()

    def elapsed_time(self):
        return time.time() - self.start_time

    def toc(self, text=""):
        if text:
            return f"{text}: {self.elapsed_time():.3f} seconds"
        else:
            return self.elapsed_time()

    def tac(self, min_sleep_s=1.0):
        remaining_time = min_sleep_s - self.elapsed_time()
        if remaining_time > 0:
            time.sleep(remaining_time)


class Word(Seed, Glass):
    """
    Defines a short string with limitations

    - Minimum length is set in Environment with default 1
    - Empty word is ``n_o_n_e``
    - Allowed characters are

        - Lower case ascii ``a-z``
        - Digits ``0-9``
        - Underscore ``_``

    - Underscore and digits can not be the first character
    - Underscore can not be the last character
    - Can not contain double underscore since it acts as separator for words
      in :class:`.Key`

    Sample words::

        "simple"

        "with_longer_name"
        "digit1"
        "longer_digit2"

    """

    logger = logging.getLogger(__name__)

    REGEX = r"(?!.*__.*)[a-z0-9][a-z_0-9]*[a-z0-9]"

    #: Allowed characters
    ALLOWED_CHARACTERS = string.ascii_lowercase + string.digits + "_"

    #: Allowed first characters
    ALLOWED_STARTSWITH = string.ascii_lowercase + string.digits

    #: Allowed last characters
    ALLOWED_ENDSWITH = string.ascii_lowercase + string.digits

    NONE = "n_o_n_e"

    @classmethod
    def is_seed(cls, str_: str):
        if len(str_) == 1:
            if MINIMUM_WORD_LENGTH > 1:
                return False
            else:
                return str_ in cls.ALLOWED_STARTSWITH
        else:
            return super().is_seed(str_)

    @classmethod
    def none(cls):
        """
        Return Word repesentation of ``None``

        :return: ``n_o_n_e``
        :rtype: Word
        """
        return cls(cls.NONE)

    @classmethod
    def from_int(cls, number):
        return cls(str(number))

    @classmethod
    def from_ints(cls, numbers):
        numstr = "_".join([str(x) for x in numbers])
        return cls(numstr)

    @classmethod
    def check(cls, word: str):
        """
        Check that string is a valid word

        :param word: String to check
        :type word: str
        :return: True if ``word`` is valid word, False if not
        :rtype: bool
        """
        if len(word) < MINIMUM_WORD_LENGTH:
            raise BadWord(
                f"Element too short. Element '{word}' has "
                f"length {len(word)}, while minimum length "
                f"is {MINIMUM_WORD_LENGTH}"
            )
        if word[0] not in cls.ALLOWED_STARTSWITH:
            raise BadWord(
                f"Invalid startswith. Word '{word}' "
                f"cannot start with '{word[0]}'. "
                f"Allowed startswith characters are: "
                f"{cls.ALLOWED_STARTSWITH}"
            )
        if word[-1] not in cls.ALLOWED_ENDSWITH:
            raise BadWord(
                f"Invalid endswith. Word '{word}' "
                f"cannot end with '{word[-1]}'. "
                f"Allowed endswith characters are: "
                f"{cls.ALLOWED_ENDSWITH}"
            )
        invalid_characters = [x for x in word if x not in cls.ALLOWED_CHARACTERS]
        if len(invalid_characters) > 0:
            raise BadWord(
                f"Invalid character(s). Word '{word}' cannot "
                f"contain any of {invalid_characters}. "
                f"Allowed characters are: "
                f"{cls.ALLOWED_CHARACTERS}"
            )
        if WORD_SEPARATOR in word:
            raise BadWord(
                f"Word contains word separator, which is "
                f"reserved for separating words in a Key."
                f"Word '{word}' cannot contain "
                f"'{CLASS_SEPARATOR}'"
            )

    @classmethod
    def elf(cls, word):
        """Attempts to interpret input as a valid word

        .. warning: Elves are fickle

        :raises AngryElf: If input cannot be interpreted as Word
        :param word: Input word string or word class
        :type word: str or Word
        :rtype: Word
        """
        if isinstance(word, Word):
            return word
        elif isinstance(word, Key):
            raise AngryElf("This is a Key, not a word. Idiot.")
        elif isinstance(word, str) and cls.is_seed(word):
            return cls(word)
        elif isinstance(word, int):
            return cls(str(word))
        elif isinstance(word, float):
            if word.is_integer():
                return cls(str(int(word)))
            return cls(str(word).replace(".", "_"))
        else:
            _orignial_class = None
            if not isinstance(word, str):
                _original_class = type(word).__name__
                word = str(word)

            _original = word

            if WORD_SEPARATOR in word:
                raise AngryElf(
                    f"This looks more like a Key: '{_original}'; "
                    f"Try the Key.elf() not me. In case you "
                    f"didn't notice I'm the Word.elf()"
                )

            # Test camel to snake
            if " " not in word and "_" not in word:
                word = Text.camel_to_snake(word)
                if cls.is_seed(word):
                    return cls(word)
                word = _original

            word = word.replace("_", " ")
            word = word.strip()
            word = word.replace(" ", "_")
            while "__" in word:
                word = word.replace("__", "_")
            word = Text.camel_to_snake(word)
            while "__" in word:
                word = word.replace("__", "_")
            if cls.is_seed(word):
                return cls(word)
            word = _original
            word = word.lower()
            new_word = ""
            for letter in word:
                if letter in cls.ALLOWED_CHARACTERS:
                    new_word += letter
                else:
                    new_word += "_"
            while "__" in new_word:
                new_word = new_word.replace("__", "_")

            while len(new_word) > MINIMUM_WORD_LENGTH:
                if new_word[0] not in cls.ALLOWED_STARTSWITH:
                    new_word = new_word[1:]
                elif new_word[-1] not in cls.ALLOWED_ENDSWITH:
                    new_word = new_word[:-1]
                else:
                    break

            if Word.is_seed(new_word):
                return Word(new_word)

            raise AngryElf(
                f"Cannot for the bleeding world figure out "
                f"how to make a Word from this sorry "
                f"excuse of a string: {_original}"
            )

    def __init__(self, word: str):
        if PIXIE:
            try:
                self.check(word)
            except BadWord as ie:
                raise PixieInPipeline(f"Invalid word: {ie}") from ie
        else:
            if not self.is_seed(word):
                raise BadWord(f"Invalid word: {word}")
        self.__word = word

    def __str__(self):
        return self.__word

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    def __hash__(self):
        return hash(self.__word)

    def __repr__(self):
        return f"Word('{self.__word}')"

    def __add__(self, other):
        if isinstance(other, str):
            return Word(f"{self}_{other}")
        elif isinstance(other, Word):
            return Key.from_words([self, other])
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return Word(f"{other}_{self}")

    @staticmethod
    def _int(element):
        try:
            return int(element)
        except ValueError:
            return None

    @classmethod
    def _is_int(cls, element):
        return cls._int(element) is not None

    def is_none(self):
        """
        Check if word is ``n_o_n_e``, i.e. word representation of ``None``

        :rtype: bool
        """
        return self.__word == self.NONE

    def is_int(self):
        """
        Check if word is an integer

        :rtype: bool
        """
        ints = self._ints()
        return len(ints) == 1 and ints[0] is not None

    def _elements(self):
        return self.__word.split("_")

    def _ints(self):
        return [self._int(x) for x in self._elements()]

    def index(self):
        """
        Get index of word

        :raises BadWord: If word is an integer and thus cannot have an index
        :return: 0 if word has no index, otherwise returns index
        :rtype: int
        """
        elements = self._elements()
        if len(elements) == 1:
            if self._is_int(elements[0]):
                raise BadWord(f"Word is an integer, cannot get index: {self}")
            return 0
        else:
            idx = elements[-1]
            if self._is_int(idx):
                return self._int(idx)
            else:
                return 0

    @classmethod
    def _is_numeric(cls, ints):
        return all(ints)

    def is_numeric(self):
        """
        Check if word is numeric, i.e. can be converted to integer

        :rtype: bool
        """
        return self._is_numeric(self._ints())

    def to_int(self):
        """
        Convert word to integer

        :raise NotAnInteger: If word is not an integer
        :rtype: int
        """
        ints = self._ints()
        if len(ints) == 1 and ints[0] is not None:
            return ints[0]
        else:
            raise NotAnInteger(f"Word is not an integer: {self}")

    def to_ints(self):
        """
        Convert word to list of integers

        :rtype: int
        """
        return self._ints()

    def increment(self):
        """
        Create a new word with index incremented

        Example::

            word = Word('my_word_2')
            word.increment()
                Word('my_word_3')

        :rtype: Word
        """
        elements = self._elements()
        if len(elements) == 1:
            if self._is_int(elements[0]):
                raise BadWord(f"Word is an integer and " f"cannot be incremented: {self}")
            elements = elements + ["1"]
        else:
            idx = self._int(elements[-1])
            if idx is None:
                elements += ["1"]
            else:
                elements[-1] = str(idx + 1)
        return Word("_".join(elements))


class Identity(Seed, Glass):
    """UUID string generator with convenience functions

    Inherits str, and is therefore an immutable string, with a fixed format
    as illustrated below.

    Examples::

        Identity()
            'BD8E446D_3EB9_4396_8173_FA1CF146203C'

        Identity.is_in('Has BD8E446D_3EB9_4396_8173_FA1CF146203C within')
            True

        Identity.find_one('Has BD8E446D_3EB9_4396_8173_FA1CF146203C within')
            'BD8E446D_3EB9_4396_8173_FA1CF146203C'

    """

    REGEX = r"[0-9A-F]{8}\_[0-9A-F]{4}\_[0-9A-F]{4}\_[0-9A-F]{4}" r"\_[0-9A-F]{12}"

    REGEX_CLASSIC = r"[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}" r"\-[0-9a-f]{12}"
    REGEX_COMPACT = r"[0-9a-f]{32}"
    LENGTH = 36

    @classmethod
    def from_seed(cls, seed: str):
        """
        Create Identity from seed string

        :rtype: Identity
        """
        return cls(seed)

    @classmethod
    def is_classic(cls, classic: str):
        """
        Check if string is uuid on classic format

        :rtype: bool
        """
        if len(classic) != 36:
            return False
        _regex_exact = rf"^{cls.REGEX_CLASSIC}$"
        return re.compile(_regex_exact).match(classic) is not None

    @classmethod
    def from_classic(cls, classic: str):
        """
        Create Identity from classic format uuid

        :rtype: Identity
        """
        classic = classic.replace("-", "_").upper()
        return cls(classic)

    @classmethod
    def is_compact(cls, compact: str):
        """
        Check if string is compact format uuid

        :rtype: bool
        """
        if len(compact) != 32:
            return False
        _regex_exact = rf"^{cls.REGEX_COMPACT}$"
        return re.compile(_regex_exact).match(compact) is not None

    @classmethod
    def from_compact(cls, compact: str):
        """
        Create identity from compact format uuid

        :rtype: Identity
        """
        compact = "_".join([compact[:8], compact[8:12], compact[12:16], compact[16:20], compact[20:]]).upper()
        return cls(compact)

    @classmethod
    def elf(cls, input):
        """
        Try to create an identity based on input

        :raises AngryElf: If an identity cannot be created
        :rtype: Identity
        """
        if isinstance(input, Identity):
            return input
        elif isinstance(input, str):
            if cls.is_seed(input):
                return cls(input)
            elif cls.is_classic(input):
                return cls.from_classic(input)
            elif cls.is_compact(input):
                return cls.from_compact(input)
            elif cls.is_classic(input.lower()):
                return cls.from_classic(input.lower())
            elif cls.is_compact(input.lower()):
                return cls.from_compact(input.lower())

            # Try to find one or more identities in string
            ids = cls.find_seeds(input)
            if len(ids) > 0:
                # If found, return the first
                return ids[0]
        raise IdentityError(f"This useless excuse for a string has no soul, " f"and hence no identity: '{input}'")

    def __init__(self, identity: Optional[str] = None):
        if not identity:
            identity = str(uuid.uuid4()).replace("-", "_").upper()
        elif not self.is_seed(identity):
            raise IdentityError(f"String is not valid identity: {identity}")
        self.__identity = identity

    def __str__(self):
        return self.__identity

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    def __hash__(self):
        return hash(self.__identity)

    def __repr__(self):
        return f"Identity('{self.__identity}')"

    def classic(self):
        """
        Return uuid string on classic format::

            Identity().classic()
                '18a9e538-3b5e-4442-b2b9-f728fbe8f240'

        :rtype: str
        """
        return self.__identity.replace("_", "-").lower()

    def compact(self):
        """
        Return uuid string on compact format::

            Identity().compact()
                '18a9e5383b5e4442b2b9f728fbe8f240'

        :rtype: str
        """
        return self.__identity.replace("_", "").lower()


class Key(Seed, Glass):
    """
    Defines key string with limitations:

    - Minimum length is 2
    - Allowed characters are:

        - Lower case ascii (a-z)
        - Digits (0-9)
        - Underscore (``_``)
        - Double underscore (``__``)

    - Underscore and digits can not be the first character
    - Underscore can not be the last character
    - The double underscore act as separator for :class:`.Word`
      in the key
    - Triple underscore is reserved for separating keys from other keys or
      seeds, such as in class :class:`.Atom`

    Sample keys::

        "simple"

        "with_longer_name"
        "digit1"
        "longer_digit2"
        "word_one__word_two__word_three"
        "word1__word2__word3"
        "word_1__word_2__word_3"

    """

    #: Allowed characters
    ALLOWED_CHARACTERS = string.ascii_lowercase + string.digits + "_"

    #: Allowed first characters
    ALLOWED_STARTSWITH = string.ascii_lowercase

    #: Allowed last characters
    ALLOWED_ENDSWITH = string.ascii_lowercase + string.digits

    #: Regular expression for verifying and finding keys
    REGEX = rf"(?!.*{CLASS_SEPARATOR}.*)[a-z][a-z_0-9]*[a-z0-9]"

    def __init__(self, key: str):
        if PIXIE:
            try:
                self.verify_key(key)
            except BadWord as ie:
                raise PixieInPipeline("Invalid word in key") from ie
            except InvalidKey as ik:
                raise PixieInPipeline("Invalid key") from ik
        if not self.is_seed(key):
            raise InvalidKey(f"Invalid key: {key}")
        self.__key = key

    def __str__(self):
        return self.__key

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"Key('{self.__key}')"

    def __iter__(self):
        yield from self.words()

    def __add__(self, other):
        if isinstance(other, Key):
            return Key.from_words(self.words() + other.words())
        elif isinstance(other, Word):
            return Key.from_words(self.words() + [other])
        elif isinstance(other, str):
            return Key.from_words(self.words() + [Word(other)])
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Word):
            return Key.from_words([other] + self.words())
        elif isinstance(other, str):
            return Key.from_words([Word(other)] + self.words())
        # else:
        #     raise

    @classmethod
    def verify_key(cls, key: str):
        """
        Verify that string is a valid key

        :param key: String to check
        :return: True if string is valid key, False if not
        """
        if not len(key) >= MINIMUM_WORD_LENGTH:
            raise InvalidKey(
                f"Key too short. Key '{key}' has length "
                f"{len(key)}, while minimum length is "
                f"{MINIMUM_WORD_LENGTH}"
            )
        if CLASS_SEPARATOR in key:
            raise InvalidKey(
                f"Key contains word reserved as class "
                f"separator. "
                f"Key '{key}' cannot contain "
                f"'{CLASS_SEPARATOR}'"
            )
        if key[0] not in cls.ALLOWED_STARTSWITH:
            raise InvalidKey(
                f"Invalid startswith. Key '{key}' "
                f"cannot start with '{key[0]}'. "
                f"Allowed startswith characters are: "
                f"{cls.ALLOWED_STARTSWITH}"
            )

        words = key.split(WORD_SEPARATOR)
        for word in words:
            Word.check(word)

    @classmethod
    def from_words(cls, *args):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                return cls(arg)
            elif isinstance(arg, tuple) or isinstance(arg, list):
                args = tuple(arg)

        args = tuple([str(x) for x in args])
        return cls(WORD_SEPARATOR.join(args))

    @classmethod
    def from_seed(cls, str_: str):
        return cls(str_)

    @classmethod
    def from_branch(cls, branch: str):
        words = [Word(x) for x in branch.split("/")]
        return cls.from_words(words)

    def words(self):
        """
        Return list of words in key

        Example::

            key = Key('some_key__with_two__no_three_elements')
            key.words()
                [Word('some_key'), Word('with_two'), Word('three_elements')]
            key.words()[0]
                Word('some_key')

        :returns: [:class:`.Word`]
        """
        return [Word(x) for x in self.parts()]

    def parts(self):
        """
        Return list of words as strings in key

        Example::

            key = Key('some_key__with_two__no_three_elements')
            key.parts()
                ['some_key', 'with_two', 'three_elements']
            key.parts()[0]
                'some_key'

        :returns: [str]
        """
        return [x for x in self.__key.split(WORD_SEPARATOR)]

    def branch(self):
        return self.with_separator("/")

    def first(self):
        return self.words()[0]

    def last(self):
        return self.words()[-1]

    def with_separator(self, separator: str):
        """Replace separator

        Example::

            key = Key('some__key_that_could_be__path')
            key.with_separator('/')
                'some/key_that_could_be/path'

        :param separator: Separator of choice
        :type separator: str
        :return: str
        """
        return separator.join([str(x) for x in self.words()])

    @classmethod
    def elf(cls, key):
        """Attempts to create a valid key based on the input

        .. warning:: Elves are fickle

        :raise AngryElf: If a valid key cannot be created
        :param key: Input key string or key class
        :type key: str or Key
        :return: Key
        """
        if isinstance(key, Key):
            return key
        elif isinstance(key, Word):
            return Key.from_words([key])
        elif isinstance(key, Atom):
            raise AngryElf("This is an Atom. Idiot.")
        elif isinstance(key, str) and Key.is_seed(key):
            return cls.from_seed(key)
        else:
            _original_class = None
            if not isinstance(key, str):
                _original_class = type(key).__name__
                key = str(key)

            if CLASS_SEPARATOR in key:
                raise AngryElf("This looks more like an Atom. Do I look " "like an Atom elf?")
            if WORD_SEPARATOR in key:
                words = [Word.elf(x) for x in key.split(WORD_SEPARATOR)]
                return Key.from_words(words)

            _original = key
            if Key.is_seed(key):
                return cls(key)
            key = key.strip()
            if Key.is_seed(key):
                return cls(key)
            key = key.replace(" ", "_")
            if Key.is_seed(key):
                return cls(key)
            key = key.lower()
            if Key.is_seed(key):
                return cls(key)
            if _original_class:
                raise InvalidKey(
                    f"Creating "
                    f"a key from '{_original_class}' is, as "
                    f"you should have known, not meant to be. "
                    f"Resulting string was: {_original}"
                )
            key = _original.lower()
            new_key = ""
            for char in key:
                if char in cls.ALLOWED_CHARACTERS:
                    new_key += char
                else:
                    new_key += "_"
            while len(new_key) > MINIMUM_WORD_LENGTH:
                if new_key[0] not in cls.ALLOWED_STARTSWITH:
                    new_key = new_key[1:]
                elif new_key[-1] not in cls.ALLOWED_ENDSWITH:
                    new_key = new_key[:-1]
                else:
                    break

            if Key.is_seed(new_key):
                return cls(new_key)

            raise InvalidKey(
                f"I tried but no way I can make a key out of " f"this sorry excuse of a string: {_original}"
            )


class Zulu(datetime.datetime, Seed, Glass):
    # TODO: Round to millisecond etc. And floor. Check Arrow how its done

    """
    Timezone aware datetime objects in UTC

    Create using constructor::

        Zulu() or Zulu.now()
            Zulu(2020, 5, 21, 20, 5, 31, 930343)

        Zulu(2020, 5, 12)
            Zulu(2020, 5, 12)

        Zulu(2020, 5, 21, 20, 5, 31)
            Zulu(2020, 5, 21, 20, 5, 31)

    :meth:`Seed.seed` is inherited from :class:`Seed` and returns a string
    on the format ``<date>T<time>u<microseconds>Z``, and is \'designed\'
    to be file name and double click friendly, as well as easily recognizable
    within some string when using regular expressions.
    Printing a Zulu object returns seed, and Zulu can be created using
    :meth:`from_seed`::

        z = Zulu(2020, 5, 12)
        print(z)
            20200512T000000u000000Z

        z.seed()
            '20200512T000000u000000Z'

        str(z)
            '20200512T000000u000000Z'

        Zulu.from_seed('20200512T000000u000000Z')
            Zulu(2020, 5, 12)

    For an `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_
    formatted string, use custom function::

        z = Zulu('20200521T202041u590718Z')
        z.iso()
            '2020-05-21T20:20:41.590718+00:00'

    Similarly, Zulu can be created from ISO string::

        Zulu.from_iso('2020-05-21T20:20:41.590718+00:00')
            Zulu(2020, 5, 21, 20, 20, 41, 590718)


    Inputs or constructors may vary, but Zulu objects are *always* UTC. Hence
    the name Zulu.

    Constructor also takes regular datetime objects, provided they have
    timezone info::

        dt = datetime.datetime(2020, 5, 23, tzinfo=pytz.utc)
        Zulu(dt)
            Zulu(2020, 5, 23, 0, 0, tzinfo=<UTC>)

        dt = datetime.datetime(2020, 5, 23, tzinfo=dateutil.tz.tzlocal())
        Zulu(dt)
            Zulu(2020, 5, 22, 22, 0, tzinfo=<UTC>)

    Zulu has element access like datetime, in addition to string convenience
    attributes::

        z = Zulu()
        print(z)
            20200522T190137u055918Z
        z.month
            5
        z.str.month
            '05'
        z.str.date
            '20200522'
        z.str.time
            '190137'

    Zulu has a method :meth:`delta` for timedelta, as well as :meth:`add`
    for adding timedeltas directly to generate a new Zulu::

        Zulu.delta(hours=1)
            datetime.timedelta(seconds=3600)

        z = Zulu(2020, 1, 1)
        z.add(days=2)
            Zulu(2020, 1, 3)

    For more flexible ways to create a Zulu object, see :meth:`Zulu.elf`

    """

    _ZuluStr = namedtuple(
        "_ZuluStr", ["year", "month", "day", "hour", "minute", "second", "microsecond", "date", "time", "seed"]
    )

    _FORMAT = "%Y%m%dT%H%M%Su%fZ"
    REGEX = r"\d{8}T\d{6}u\d{6}Z"
    LENGTH = 23

    ISO_REGEX_STRING = (
        r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-"
        r"(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):"
        r"([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-]"
        r"(?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    )
    ISO_REGEX = re.compile(ISO_REGEX_STRING)

    ############################################################################
    # String methods
    ############################################################################

    @classmethod
    def is_iso(cls, st: str):
        """
        Check if input string is
        `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_

        Check is done using regex :data:`Zulu.ISO_REGEX`

        :param st: Maybe an ISO formatted string
        :return: True if input string is iso, False if not
        :rtype: bool
        """

        return cls.ISO_REGEX.match(st) is not None

    ############################################################################
    # Timezone methods
    ############################################################################

    @classmethod
    def all_timezones(cls):
        """
        Returns a list of all allowed timezone names

        Timezone \'local\' will return a datetime object with local timezone,
        but is not included in this list

        Wrapper for :meth:`pytz.all_timezones`

        :return: List of timezones
        :rtype: list
        """
        return pytz.all_timezones

    @classmethod
    def _to_utc(cls, ts):
        return ts.astimezone(pytz.utc)

    @classmethod
    def _tz_from_name(cls, tz="utc"):
        if tz == "local":
            tz = dateutil.tz.tzlocal()  # type: ignore
        else:
            try:
                tz = pytz.timezone(tz)
            except pytz.exceptions.UnknownTimeZoneError:
                raise ZuluError(
                    f"Unknown timezone: '{tz}'. " f"Use Zulu.all_timezones() for a list " f"of actual timezones"
                )
        return tz

    ############################################################################
    # Create methods
    ############################################################################

    @classmethod
    def now(cls, tz=None):
        """
        Overrides ``datetime.datetime.now()``. Equivalent to ``Zulu()``

        :raise ZuluError: If parameter ``tz`` has a value. Even if value is UTC
        :param tz: Do not use. Zulu is always UTC
        :return: Zulu
        """
        if tz:
            raise ZuluError("Zulu.now() does not allow input time zone info. " "Zulu is always UTC. Hence the name")
        return cls()

    @classmethod
    def _from_unaware(cls, ts, tz=None):
        if not tz:
            raise ZuluError(
                "No timezone info. Set timezone to use "
                "with 'tz=<timezone string>'. 'local' will "
                "use local timezone info. Use "
                "Zulu.all_timezones() for a list of actual "
                "timezones"
            )
        return ts.replace(tzinfo=cls._tz_from_name(tz))

    @classmethod
    def _elf(cls, ts, tz=None):
        # Takes a datetime.datetime object and adds the input tzinfo if
        # none is present
        if not ts.tzinfo:
            ts = cls._from_unaware(ts, tz=tz)
        return ts

    @classmethod
    def from_unaware(cls, ts, tz="utc"):
        """Create Zulu from timezone unaware datetime

        :param ts: Unaware time stamp
        :type ts: datetime.datetime
        :param tz: Time zone, with 'utc' as default.
            'local' will use local time zone
        :rtype: Zulu
        """
        if ts.tzinfo:
            raise ZuluError(f"Input datetime already has " f"time zone info: {ts}. " f"Use constructor or Zulu.elf()")
        else:
            ts = cls._from_unaware(ts, tz=tz)
        return cls(ts)

    @classmethod
    def from_unaware_local(cls, ts):
        """
        Create Zulu from timezone unaware local timestamp

        :param ts: Timezone unaware datetime
        :type ts: datetime.datetime
        :rtype: Zulu
        """
        return cls.from_unaware(ts, tz="local")

    @classmethod
    def from_unaware_utc(cls, ts):
        """
        Create Zulu from timezone unaware UTC timestamp

        :param ts: Timezone unaware datetime
        :type ts: datetime.datetime
        :rtype: Zulu
        """
        return cls.from_unaware(ts, tz="utc")

    @classmethod
    def _parse_iso(cls, iso: str):
        ts = dateparser(iso)
        if ts.tzinfo and str(ts.tzinfo) == "tzutc()":
            ts = ts.astimezone(pytz.utc)
        return ts

    @classmethod
    def from_iso(cls, str_: str, tz=None):
        """
        Create Zulu object from ISO 8601 string

        :param str_: ISO 8601 string
        :param tz: Timezone string to use if missing in ts_str
        :return: Zulu
        :rtype: Zulu
        """
        ts = cls._parse_iso(str_)
        if tz and not ts.tzinfo:
            ts = cls._from_unaware(ts, tz)
        elif ts.tzinfo and tz:
            raise ZuluError(
                "Timezone info found in ISO string as well as "
                "input timezone argument (tz). Keep tz=None, "
                "or use Zulu.elf()"
            )
        elif not tz and not ts.tzinfo:
            raise ZuluError("No timezone info in neither ISO string " "nor tz argument")
        return cls(ts)

    @classmethod
    def _parse(cls, ts_str: str, pattern: str):
        return datetime.datetime.strptime(ts_str, pattern)

    @classmethod
    def parse(cls, ts_str: str, pattern: str, tz=None):
        """Parse time stamp string with the given pattern

        :param ts_str: Timestamp string
        :type ts_str: str
        :param pattern: Follows standard
            `python strftime reference <https://strftime.org/>`_
        :param tz: Timezone to use if timestamp does not have timezone info
        :return: Zulu
        """
        ts = cls._parse(ts_str, pattern)
        if not ts.tzinfo:
            ts = cls._from_unaware(ts, tz=tz)
        elif tz:
            raise ZuluError(
                "Cannot have an input timezone argument when " "input string already has timezone information"
            )
        return cls(ts)

    @classmethod
    def from_seed(cls, seed: str):
        """
        Create Zulu object from seed string

        :param seed: Seed string
        :rtype: Zulu
        """
        if not cls.is_seed(seed):
            raise ZuluError(f"String is not Zulu seed: {seed}")
        ts = cls._parse(seed, cls._FORMAT)
        ts = cls._from_unaware(ts, tz="utc")
        return cls(ts)

    @classmethod
    def _from_epoch(cls, epoch):
        return datetime.datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.UTC)

    @classmethod
    def from_epoch(cls, epoch):
        """
        Create Zulu object from UNIX Epoch

        :param epoch: Unix epoch
        :type epoch: float
        :return: Zulu instance
        :rtype: Zulu
        """
        ts = cls._from_epoch(epoch)
        return cls(ts)

    @classmethod
    def _fill_args(cls, args):
        if len(args) < 8:
            # From date
            args = list(args)
            args += (8 - len(args)) * [0]
            if args[1] == 0:
                args[1] = 1
            if args[2] == 0:
                args[2] = 1
            args = tuple(args)

        if args[-1] not in [None, 0, pytz.utc]:
            raise ZuluError(f"Zulu can only be UTC. " f"Invalid timezone: {args[-1]}")

        args = list(args)
        args[-1] = pytz.utc
        return tuple(args)

    @classmethod
    def glass(cls, *args, **kwargs):
        if len(kwargs) == 0 and len(args) == 1:
            if isinstance(args[0], Zulu):
                return args[0]
            elif isinstance(args[0], str):
                return cls.from_str(args[0])
        else:
            return cls(*args, **kwargs)

    @classmethod
    def elf(cls, *args, tz="local"):
        """
        General input Zulu constructor

        Takes the same inputs as constructor, and also allows Zulu
        objects to pass through. If timeozone is missing it will assume the input
        timezone ``tz``, which is set to local as default

        It takes both seed strings and iso strings::

            Zulu.elf('20201112T213732u993446Z')
                Zulu(2020, 11, 12, 21, 37, 32, 993446)

            Zulu.elf('2020-11-12T21:37:32.993446+00:00')
                Zulu(2020, 11, 12, 21, 37, 32, 993446)

        It takes UNIX epoch::

            e = Zulu(2020, 1, 1).epoch()
            e
                1577836800.0
            Zulu.elf(e)
                Zulu(2020, 1, 1)

        It will guess the missing values if input integers are not a full date
        and/or time::

            Zulu.elf(2020)
                Zulu(2020, 1, 1)

            Zulu.elf(2020, 2)
                Zulu(2020, 2, 1)

            Zulu.elf(2020,1,1,10)
                Zulu(2020, 1, 1, 10, 0, 0)

        .. warning:: Elves are fickle

        :raise AngryElf: If an instance cannot be created from the given input
        :param args: Input arguments
        :param tz: Time zone to assume if missing. 'local' will use local
            time zone. Use :meth:`all_timezones` for a list of actual
            timezones. Default is 'local'
        :return: Best guess Zulu object
        :rtype: Zulu
        """
        ts = None
        if len(args) == 0:
            return cls()
        elif len(args) > 1:
            args = cls._fill_args(args)
            ts = datetime.datetime(*args)
            if not ts.tzinfo:
                ts = cls._from_unaware(ts, tz)
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, Zulu):
                return arg
            elif isinstance(arg, datetime.datetime):
                # Add timzone if missing
                ts = cls._elf(arg, tz=tz)
                return cls(ts)
            elif isinstance(arg, float):
                return cls.from_epoch(arg)
            elif isinstance(arg, int):
                # Instantiate as start of year
                return cls(arg, 1, 1)
            elif isinstance(arg, str):
                if cls.is_seed(arg):
                    return cls.from_seed(arg)
                elif cls.is_iso(arg):
                    ts = cls._parse_iso(arg)
                    # Add timzone if missing
                    ts = cls._elf(ts, tz=tz)
                else:
                    raise ZuluError(
                        f"String is neither zulu, nor ISO: {arg}. "
                        f"Use Zulu.parse() and enter the format "
                        f"yourself"
                    )
            else:
                raise ZuluError(f"Found no way to interpret input " f"argument as Zulu: {arg} [{type(arg)}]")
        return cls(ts)

    @classmethod
    def range(cls, start=None, n=10, delta=datetime.timedelta(hours=1)):
        """Generate a list of Zulu of fixed intervals

        .. note:: Mainly for dev purposes. There are far better
            ways of creating a range of timestamps, such as using pandas.

        :param start: Start time Zulu, default is *now*
        :type start: Zulu
        :param n: Number of timestamps in range, with default 10
        :type n: int
        :param delta: Time delta between items, with default one hour
        :type delta: datetime.timedelta
        :rtype: [Zulu]
        """
        if not start:
            start = cls()
        return [Zulu.elf(start + x * delta) for x in range(n)]

    def __new__(cls, *args, **kwargs):
        if len(args) == 0 and len(kwargs) == 0:
            ts = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        elif len(args) == 1 and len(kwargs) == 0:
            arg = args[0]
            if isinstance(arg, str):
                raise ZuluError(
                    "Cannot instantiate Zulu with a string. Use "
                    "Zulu.from_iso(), Zulu.from_seed(), "
                    "Zulu.from_string() or Zulu.parse()"
                )
            elif isinstance(arg, float):
                raise ZuluError(
                    f"Cannot create Zulu object from a float: "
                    f"{arg}; If float is unix epoch, "
                    f"use Zulu.from_epoch()"
                )
            elif isinstance(arg, Zulu):
                raise ZuluError(f"Input argument is already Zulu: {arg}. " f"Use Zulu.glass() to allow passthrough")
            elif isinstance(arg, datetime.datetime):
                ts = arg
                if not ts.tzinfo:
                    raise ZuluError(
                        "Cannot create Zulu from datetime if "
                        "datetime object does not have timezone "
                        "info. Use Zulu.from_unaware()"
                    )
                ts = ts.astimezone(pytz.UTC)
            else:
                raise ZuluError(f"Unable to interpret input argument: " f"{arg} [{type(arg).__name__}]")
        else:
            # Handle input as regular datetime input (year, month, day etc)
            try:
                ts = datetime.datetime(*args)
            except TypeError as te:
                raise ZuluError from te
            # Add timezone info if missing (assume utc, of course)
            if not ts.tzinfo:
                ts = ts.replace(tzinfo=pytz.UTC)

        # Create actual object
        args = tuple([ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, ts.microsecond, ts.tzinfo])
        self = super().__new__(cls, *args)
        seed = self.strftime(self._FORMAT)
        self.str = self._ZuluStr(  # type: ignore
            year=seed[:4],
            month=seed[4:6],
            day=seed[6:8],
            hour=seed[9:11],
            minute=seed[11:13],
            second=seed[13:15],
            microsecond=seed[16:22],
            date=seed[:8],
            time=seed[9:15],
            seed=seed,
        )
        return self

    def __str__(self):
        return self.str.seed  # type: ignore

    def __repr__(self):
        times = [self.hour, self.minute, self.second]
        has_micro = self.microsecond > 0
        has_time = sum(times) > 0
        nums = [self.year, self.month, self.day]
        if has_time or has_micro:
            nums += times
        if has_micro:
            nums += [self.microsecond]
        numstr = ", ".join([str(x) for x in nums])
        return f"Zulu({numstr})"

    def epoch(self):
        """
        Get UNIX epoch (seconds since January 1st 1970)

        Wrapper for :meth:`datetime.datetime.timestamp`

        :return: Seconds since January 1st 1970
        :rtype: float
        """
        return self.timestamp()

    @classmethod
    def from_str(cls, st: str):
        """
        Converts seed or iso string to Zulu

        :param st: Seed or iso string
        :rtype: Zulu
        """
        if cls.is_seed(st):
            return cls.from_seed(st)
        elif cls.is_iso(st):
            return cls.from_iso(st)
        else:
            raise ZuluError(
                f"Unknown string format (neither seed nor iso): "
                f"{st}; "
                f"Use Zulu.parse() to specify format pattern and "
                f"timezone"
            )

    def iso(self, full=False):
        """Create `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ string

        Example::

            z = Zulu(2020, 5, 21)
            z.iso()
                '2020-05-21T00:00:00+00:00'

            z.iso(full=True)
                '2020-05-21T00:00:00.000000+00:00'

        :param full: If True, pad isostring to full length when microsecond is
            zero, so that all strings returned will have same length (has
            proved an issue with a certain document database tool, which
            was not able to parse varying iso string length without help)
        :type full: bool
        :return: str
        """
        iso = self.isoformat()
        if full:
            if len(iso) == 25:
                iso = iso.replace("+", ".000000+")
        return iso

    def format(self, pattern):
        """
        Format Zulu to string with the given pattern

        Wrapper for :meth:`datetime.datetime.strftime`

        :param pattern: Follows standard
            `Python strftime reference <https://strftime.org/>`_
        :return: str
        """
        return self.strftime(pattern)

    def to_unaware(self):
        """
        Get timezone unaware datetime object in UTC

        :return: Timezone unaware datetime
        :rtype: datetime.datetime
        """
        ts = datetime.datetime.utcfromtimestamp(self.epoch()).replace(tzinfo=pytz.UTC)
        return ts.replace(tzinfo=None)

    def to_tz(self, tz="local"):
        """Create regular datetime with input timezone

        For a list of timezones use :meth:`.Zulu.all_timezones()`.
        'local' is also allowed, although not included in the list

        :param tz: Time zone to use. 'local' will return the local time zone.
            Default is 'local'
        :rtype: datetime.datetime
        """
        ts_utc = datetime.datetime.utcfromtimestamp(self.epoch()).replace(tzinfo=pytz.UTC)
        return ts_utc.astimezone(self._tz_from_name(tz))

    def to_local(self):
        """Create regular datetime with local timezone

        :rtype: datetime.datetime
        """
        return self.to_tz(tz="local")

    def round_to_ms(self, floor=False):
        """Round to nearest millisecond

        :rtype: Zulu
        """
        mod = self.microsecond % 1000
        if mod == 0:
            return self
        elif floor or mod < 500:
            return self.add(microseconds=-mod)
        else:
            return self.add(microseconds=1000 - mod)

    def floor_to_ms(self):
        return self.round_to_ms(floor=True)

    def round_to_s(self, floor=False):
        """Round to nearest second

        :rtype: Zulu
        """
        if self.microsecond == 0:
            return self
        elif floor or self.microsecond < 50000:
            return self.add(microseconds=-self.microsecond)
        else:
            return self.add(seconds=1, microseconds=-self.microsecond)

    def floor_to_s(self):
        return self.round_to_s(floor=True)

    @classmethod
    def delta(cls, days=0, hours=0, minutes=0, seconds=0, microseconds=0, weeks=0):
        """Wrapper for :meth:`datetime.timedelta`

        :param days: Number of days
        :param hours: Number of hours
        :param minutes: Number of minutes
        :param seconds: Number of seconds
        :param microseconds: Number of microseconds
        :param weeks: Number of weeks
        :return: datetime.timedelta
        """
        return datetime.timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds, weeks=weeks
        )

    def add(self, days=0, hours=0, minutes=0, seconds=0, microseconds=0, weeks=0):
        """
        Adds the input to current Zulu object and returns a new one

        :param days: Number of days
        :param hours: Number of hours
        :param minutes: Number of minutes
        :param seconds: Number of seconds
        :param microseconds: Number of microseconds
        :param weeks: Number of weeks

        :return: Current object plus added delta
        :rtype: Zulu
        """
        delta = self.delta(
            days=days, hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds, weeks=weeks
        )
        return self + delta


# TODO: Add DocAtom class, which includes atom conversion to dictionary both ways (or seed, if set)
class Atom(Doc, Seed, Glass):
    """
    Triplet identifier intended for objects and data sets alike

    Format: ``<zulu>___<key>___<identity>``

    :class:`.Zulu` represents t0 or creation time

    :class:`.Key` defines grouping of the contents

    :class:`.Identity` is a unique identifier for the contents

    Constructor initializes a valid atom, and will raise an ``AtomError``
    if a valid atom cannot be created based on input parameters.

    The constructor must as minimum have :class:`.Key` as input, although
    string version (seed) of key is allowed::

        atom = Atom('zaphod__ship_33__inventory')
        atom.key()
            'zaphod__ship_33__inventory'
        atom.zulu()
            Zulu(2020, 5, 22, 13, 13, 18, 179169, tzinfo=<UTC>)
        atom.identity()
            '060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

    Output methods::

        atom = Atom('zaphod__ship_33__inventory',
                    zulu=Zulu(2020, 5, 22, 13, 13, 18, 179169),
                    identity=Identity('060AFBD5_D865_4974_8E37_FDD5C55E7CD8'))

        str(atom)
            '20200522T131318u179169Z___zaphod__ship_33__inventory___060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

        atom.seed()
            '20200522T131318u179169Z___zaphod__ship_33__inventory___060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

        atom.to_dict()
            {
                'zulu': Zulu(2020, 5, 22, 13, 13, 18, 179169),
                'key': Key('zaphod__ship_33__inventory'),
                'identity': Identity('060AFBD5_D865_4974_8E37_FDD5C55E7CD8')
            }

    Atom inherits :class:`.Doc` and therefore has a ``to_doc()`` method::

        atom.to_doc()
            {
                'zulu': '2020-05-22T13:13:18.179169+00:00',
                'key': 'zaphod__ship_33__inventory',
                'identity': '060AFBD5_D865_4974_8E37_FDD5C55E7CD8'
            }

    The ``to_doc()`` is used for output to the equivalent ``to_json()`` and
    ``to_yaml()``, with equivalent methods for creating an instance from
    ``dict``, doc or a JSON or YAML file.

    When storing an atom as part of another dictionary,
    the most compact method would however be ``seed``, unless readability
    is of importance.

    """

    REGEX = (
        r"\d{8}T\d{6}u\d{6}Z\_\_\_[a-z][a-z_0-9]*[a-z0-9]\_\_\_"
        r"[0-9A-F]{8}\_[0-9A-F]{4}\_[0-9A-F]{4}\_[0-9A-F]{4}\_[0-9A-F]{12}"
    )

    @classmethod
    def from_seed(cls, seed: str):
        """Creates an Atom from a seed string

        :param seed: A valid atom seed string
        :rtype: Atom
        """
        if not cls.is_seed(seed):
            raise AtomError(f"Invalid atom seed: {seed}")
        zulu, key, identity = seed.split(CLASS_SEPARATOR)
        return cls(key=Key(key), zulu=Zulu.from_seed(zulu), identity=Identity(identity))

    @classmethod
    def elf(cls, *args, **kwargs):
        """Attempts to create an atom based on the input arguments

        .. warning:: Elves are fickle

        :raise AngryElf: If input arguments cannot be converted to Atom
        :rtype: Atom
        """
        if len(args) == 1 and not kwargs:
            arg = args[0]
            if isinstance(arg, Atom):
                return arg
            if isinstance(arg, Key):
                return cls(arg)
            elif isinstance(arg, str):
                if Key.is_seed(arg):
                    return cls(arg)
                elif cls.is_seed(arg):
                    return cls.from_seed(arg)
                else:
                    raise AtomError(f"This input string is nowhere near " f"what I need to create an Atom: {arg}")
            elif Key.is_seed(arg):
                return cls(arg)
            else:
                raise AtomError(
                    f"How the fuck am I supposed to create an atom "
                    f"based on this ridiculous excuse for an "
                    f"input: {arg} [{type(arg)}]"
                )
        elif len(args) == 0:
            if "key" not in kwargs:
                raise AtomError(
                    "At the very least, give me a key to work "
                    "on. You know, key as thoroughly described "
                    "in class Key"
                )
            key = Key.elf(kwargs["key"])
            identity = None
            zulu = None
            if "identity" in kwargs:
                identity = Identity.elf(kwargs["identity"])
            if "zulu" in kwargs:
                zulu = Zulu.elf(kwargs["zulu"])
            return cls(key, zulu=zulu, identity=identity)
        raise AtomError(
            f"This is rubbish. Cannot make any sense of this "
            f"mindless junk of input: "
            f"args={args}; kwargs={kwargs}"
        )

    @classmethod
    def from_dict(cls, di: dict):
        """
        Create :class:`Atom` from input dictionary

        :param di: Input dictionary
        :rtype: Atom
        """
        return cls(key=di["key"], zulu=di["zulu"], identity=di["identity"])

    def __init__(self, key, zulu: Optional[Zulu] = None, identity: Optional[Identity] = None):
        """Atom constructor

        :param key: Valid Key
        :param zulu: Valid Zulu or None
        :param identity: Valid Identity or None
        :raise AtomError: If key is missing or any arguments are invalid
        :rtype: Atom
        """
        super().__init__()
        if isinstance(key, str):
            if Key.is_seed(key):
                key = Key(key)
            elif Atom.is_seed(key):
                raise AtomError("Cannot instantiate Atom with seed. " "Use Atom.from_seed()")
            else:
                raise AtomError(f"Invalid key: {key} [{type(key).__name__}]")

        if not isinstance(key, Key):
            raise AtomError(f"Invalid key: [{type(key)}] {key}")

        if not zulu:
            zulu = Zulu()
        if not identity:
            identity = Identity()

        self.__zulu = zulu
        self.__key = key
        self.__identity = identity

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return CLASS_SEPARATOR.join([str(self.__zulu), str(self.__key), str(self.__identity)])

    def __repr__(self):
        return f"Atom('{self.__key}', " f"zulu={self.__zulu.__repr__()}, " f"identity={self.__identity.__repr__()})"

    def __hash__(self):
        return hash((self.__zulu, self.__key, self.__identity))

    def __lt__(self, other):
        return (self.__zulu, self.__key, self.__identity) < (other.__zulu, other.__key, other.__identity)

    def __gt__(self, other):
        return (self.__zulu, self.__key, self.__identity) > (other.__zulu, other.__key, other.__identity)

    def key(self):
        """
        Get Atom Key

        :rtype: Key
        """
        return self.__key

    def zulu(self):
        """
        Get Atom Zulu

        :rtype: Zulu
        """
        return self.__zulu

    def identity(self):
        """
        Get Atom Identity

        :rtype: Identity
        """
        return self.__identity

    def to_dict(self, ignore_private: bool = True, recursive: bool = False):
        """Get Atom dict

        Example from class documentantion::

            atom.to_dict()
                {
                    'zulu': Zulu(2020, 5, 22, 13, 13, 18, 179169),
                    'key': Key('zaphod__ship_33__inventory'),
                    'identity': Identity('060AFBD5_D865_4974_8E37_FDD5C55E7CD8')
                }

        :param ignore_private: Ignore private attributes (not relevant)
        :param recursive: Recursive dicts (not relevant)
        :rtype: dict

        """
        di = super().to_dict(ignore_private=ignore_private, recursive=recursive)
        di["zulu"] = self.__zulu
        di["key"] = self.__key
        di["identity"] = self.__identity
        return di

    def to_doc(self, ignore_private: bool = True):
        """Get Atom as a serializable dictionary

        Example from class documentantion::

            atom.to_doc()
                {
                    'zulu': '2020-05-22T13:13:18.179169+00:00',
                    'key': 'zaphod__ship_33__inventory',
                    'identity': '060AFBD5_D865_4974_8E37_FDD5C55E7CD8'
                }

        :param ignore_private: Ignore private attributes (not relevant)
        :rtype: dict

        """
        doc = self.to_dict(ignore_private=ignore_private)
        doc["zulu"] = doc["zulu"].iso()
        doc["key"] = doc["key"].seed()
        doc["identity"] = doc["identity"].seed()
        return doc

    @classmethod
    def from_doc(cls, doc: dict):
        """
        Create Atom from serializable dictionary

        :param doc: Dictionary with serialized objects
        :rtype: Atom
        """
        return cls(zulu=Zulu.from_iso(doc["zulu"]), key=Key(doc["key"]), identity=Identity(doc["identity"]))

    def with_sep(self, sep: str):
        """Atom seed string with custom separator

        Example::

            atom.with_sep('/')
                '20200522T131318u179169Z/zaphod__ship_33__inventory/060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

        :param sep: Custom separator
        :rtype: str
        """
        return sep.join(str(self).split(CLASS_SEPARATOR))

    @classmethod
    def element_count(cls, elements: Optional[int] = None):
        """
        Count number of elements represented by element input

        For examples, see:

            :meth:`.Atom.key_elements()`
            :meth:`.Atom.date_elements()`
            :meth:`.Atom.time_elements()`

        :param elements: Element parameter
        :rtype: int
        """
        if elements is None or elements < 0:
            return 1
        else:
            return elements

    @classmethod
    def _elements(cls, parts, level, sep=""):
        if level == 0:
            return []
        elif level > 0:
            return parts[:level]
        else:
            return [sep.join(parts[:-level])]

    def key_elements(self, elements=None):
        """
        Get selected key elements

        Intented usage is creating sub folders for files with atom naming

        Examples::

            atom.key_elements(None)
                ['zaphod__ship_33__inventory']
            atom.element_count(None)
                1

            atom.key_elements(0)
                []
            atom.element_count(0)
                0

            atom.key_elements(2)
                ['zaphod', 'ship_33']
            atom.element_count(2)
                2

            atom.key_elements(-2)
                ['zaphod__ship_33']
            atom.element_count(-2)
                1

        :param elements: Elements
        :return: Elements
        :rtype: list
        """
        if elements is None:
            return [str(self.__key)]
        return self._elements(self.__key.words(), elements, sep=WORD_SEPARATOR)

    def date_elements(self, elements=3):
        """
        Get selected date elements

        Intented usage is creating sub folders for files with atom naming

        Examples::

            atom.date_elements(None)
                ['20200522']
            atom.element_count(None)
                1

            atom.date_elements(0)
                []
            atom.element_count(0)
                0

            atom.date_elements(2)
                ['2020', '05']
            atom.element_count(2)
                2

            atom.date_elements(-2)
                ['202005']
            atom.element_count(-2)
                1

        :param elements: Elements
        :return: Elements
        :rtype: list
        """

        if elements is None:
            return [self.__zulu.str.date]  # type: ignore
        return self._elements([self.__zulu.str.year, self.__zulu.str.month, self.__zulu.str.day], elements)  # type: ignore

    def time_elements(self, elements=0):
        """
        Get selected time elements

        Intented usage is creating sub folders for files with atom naming

        Examples::

            atom.time_elements(None)
                ['131318']
            atom.element_count(None)
                1

            atom.time_elements(0)
                []
            atom.element_count(0)
                0

            atom.time_elements(2)
                ['13', '13']
            atom.element_count(2)
                2

            atom.time_elements(-2)
                ['1313']
            atom.element_count(-2)
                1

        :param elements: Elements
        :return: Elements
        :rtype: list
        """
        if elements is None:
            return [self.__zulu.str.time]  # type: ignore
        return self._elements([self.__zulu.str.hour, self.__zulu.str.minute, self.__zulu.str.second], elements)  # type: ignore


class Waiter:
    """
    Convenience class for waiting or sleeping
    """

    @classmethod
    def sleep(cls, seconds):
        """
        Simple sleep

        :param seconds: Seconds to sleep
        """
        time.sleep(seconds)

    def __init__(self, keyboard_interrupt=True):
        self._come = Event()
        if keyboard_interrupt:
            for sig in ("SIGTERM", "SIGHUP", "SIGINT"):
                signal.signal(getattr(signal, sig), self._keyboard_interrupt)

    def wait(self, seconds):
        """
        Sleeps for the given time, can be aborted with :meth:`come` and
        exits gracefully with keyboard interrupt

        :param seconds: Seconds to wait
        :type seconds: float
        :return: True if interrupted, False if not
        :rtype: bool
        """
        self._come.clear()
        self._come.wait(seconds)
        return self._come.is_set()

    def _keyboard_interrupt(self, signo, _frame):
        self._come.set()

    def come(self):
        """
        Abort :meth:`wait`
        """
        self._come.set()


#######################################################################################
# File System
#######################################################################################


# TODO: Add the lack of speed in documentation. Not meant to be used
# for large folders (thats the whole point)
class Path(Glass):
    """Absolute paths as an instance with convenience functions

    Intended use via subclasses :class:`.Folder` and :class:`.File`

    No relative paths are allowed. Paths not starting with a valid
    mountpoint will be based in current folder

    All backslashes are replaced with :data:`FOLDER_SEPARATOR`
    """

    logger = logging.getLogger(__name__)

    FOLDER_SEPARATOR = "/"
    PATH_CHARACTER_LIMIT = 256

    LINUX = "linux"
    WINDOWS = "windows"
    OSX = "osx"
    PLATFORM = {"linux": LINUX, "linux2": LINUX, "darwin": OSX, "win32": WINDOWS}

    try:
        # Import psutil if it exists. This makes it possible
        # to use this module on Windows without installing psutil,
        # which again requires Visual Studio C++ Build Tools
        from psutil import disk_partitions  # type: ignore

        __disk_partitions = disk_partitions
    except ModuleNotFoundError:
        __disk_partitions = None

    @classmethod
    def platform(cls):
        """
        Get platform name alias

            - :data:`WINDOWS`
            - :data:`LINUX`
            - :data:`OSX`

        Example on a linux platform::

            Path.platform()
                'linux'

            Path.platform() == Path.LINUX
                True

        :raises PathError: If platform is unknown
        :return: Platform name alias
        :rtype: str
        """
        if platform in cls.PLATFORM:
            return cls.PLATFORM[platform]
        else:
            raise PathError(f"Unknown platform {platform}. " f"Known platforms are: {cls.PLATFORM.keys()}")

    @classmethod
    def host(cls):
        """Get host name

        Wrapper for ``socket.gethostname()``

        :return: Host name
        :rtype: str
        """
        return socket.gethostname()

    @classmethod
    def _join(cls, *args):
        return os.path.join(*args)

    @classmethod
    def join(cls, *args):
        """Join strings to path

        Wrapper for ``os.path.join()``

        Relative paths will include current folder::

            Path.current()
                '/Users/zaphod/dev'
            Path.join('code', 'donald')
                '/Users/zaphod/dev/code/donald'

        :return: Joined path as absolute path
        :rtype: Path
        """
        return cls(cls._join(*args))

    @classmethod
    def mountpoints(cls):
        # TODO: Add limit on levels or something to only get relevant partitions
        """List valid mountpoints/partitions or drives

        Finds mountpoints/partitions on linux/osx, and drives (C:, D:) on
        windows.

        .. warning:: Windows requires installing package with an extra:
            ``mjooln[mp]``.
            Alternatively, install package ``psutil`` manually

        .. warning:: Network drives on windows will not be found by this method,
            unless they have been mapped

        .. note:: Requires installation of Visual Studio C++ Build Tools on Windows.
            Go to the download page
            and find the Build Tools download (this is why the package
            ``psutil`` is not included by default on Windows)

        :return: Valid mountpoints or drives
        :rtype: list
        """
        if cls.__disk_partitions is None:
            raise PathError(
                "Method requires module 'psutil' "
                "installed. The module is not included in "
                "requirements since it requires "
                "Visual Studio C++ Build Tools on Windows. If "
                "you are not using Windows, simply install "
                "this package as mjooln[mountpoints]"
                "package handler. If you are on Windows, go "
                "to https://visualstudio.microsoft.com/downloads/ "
                "and find the Build Tools download"
            )

        mps = [
            Folder(x.mountpoint.replace("\\", cls.FOLDER_SEPARATOR))
            for x in cls.__disk_partitions(all=True)
            if os.path.isdir(x.mountpoint)
        ]
        # Remove duplicates (got double instance of root in a terraform vm)
        return list(set(mps))

    @classmethod
    def has_valid_mountpoint(cls, path_str):
        """Flags if the path starts with a valid mountpoint

        Wrapper for ``os.path.isabs()``

        :return: True if path has valid mountpoint, False if not
        :rtype: bool
        """
        if cls.platform() == cls.WINDOWS and cls.is_network_drive(path_str):
            return True
        return os.path.isabs(path_str)

    @classmethod
    def listdir(cls, path_str):
        """
        List folder content as plain strings with relative path names

        Wrapper for ``os.listdir()``

        Other list and walk methods in :class:`Folder` will instantiate
        :class:`File` or :class:`Folder` objects. They are thus a bit slower

        :param path_str: String with path to folder
        :return: List of relative path strings
        """
        return os.listdir(path_str)

    @classmethod
    def validate(cls, path_str):
        """
        Check if path is longer than :data:`PATH_CHARACTER_LIMIT`, which
        on Windows may cause problems

        :param path_str: Path to check
        :type path_str: str
        :raises PathError: If path is too long
        """
        if len(path_str) > cls.PATH_CHARACTER_LIMIT:
            raise PathError(
                f"Path exceeds {cls.PATH_CHARACTER_LIMIT} "
                f"characters, which may cause problems on "
                f"some platforms"
            )
        # TODO: Add check on characters in path

    def __init__(self, path: str):
        if PIXIE and not isinstance(path, str):
            raise PixieInPipeline("Input to Path constructor " "must be of type str")
        if path.startswith("~"):
            path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = path.replace("\\", self.FOLDER_SEPARATOR)
            path = os.path.abspath(path)
        path = path.replace("\\", self.FOLDER_SEPARATOR)
        if PIXIE:
            try:
                self.validate(path)
            except PathError as pe:
                raise PixieInPipeline(f"Invalid path: {path}") from pe
        self.__path = path

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return self.__path

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    # Make pandas (and other libraries) recognize Path class as pathlike
    def __fspath__(self):
        return str(self)

    def __repr__(self):
        return f"Path('{self.__path}')"

    def _rename(self, new_path: str):
        self.__path = new_path

    def as_file(self):
        """
        Create :class:`File` with same path

        :rtype: File
        """
        return File(self.__path)

    def as_folder(self):
        """
        Create :class:`Folder` with same path

        :rtype: Folder
        """
        return Folder(self.__path)

    def as_path(self):
        """
        Get as ``pathlib.Path`` object

        :return: path
        :rtype: pathlib.Path
        """
        return Path_(str(self))

    def as_pure_path(self):
        """
        Get as ``pathlib.PurePath`` object

        :return: path
        :rtype: pathlib.PurePath
        """
        return PurePath(str(self))

    def name(self):
        """Get name of folder or file

        Example::

            p = Path('/Users/zaphod')
            p
                '/Users/zaphod
            p.name()
                'zaphod'

            p2 = Path(p, 'dev', 'code', 'donald')
            p2
                '/Users/zaphod/dev/code/donald'
            p2.name()
                'donald'

            p3 = Path(p, 'dev', 'code', 'donald', 'content.txt')
            p3
                '/Users/zaphod/dev/code/donald/content.txt'
            p3.name()
                'content.txt'

        :return: Folder or file name
        :rtype: str
        """
        return os.path.basename(str(self))

    def volume(self):
        """Return path volume

        Volume is a collective term for mountpoint, drive and network drive

        :raises PathError: If volume cannot be determined
        :return: Volume of path
        :rtype: Folder
        """
        try:
            return self.network_drive()
        except PathError:
            pass
        path = os.path.abspath(str(self))
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return Folder(path)

    def exists(self):
        """Check if path exists

        Wrapper for ``os.path.exists()``

        :return: True if path exists, False otherwise
        :rtype: bool
        """
        return os.path.exists(self)

    def raise_if_not_exists(self):
        """Raises an exception if path does not exist

        :raises PathError: If path does not exist
        """
        if not self.exists():
            raise PathError(f"Path does not exist: {self}")

    def is_volume(self):
        """
        Check if path is a volume

        Volume is a collective term for mountpoint, drive and network drive

        :raises PathError: If path does not exist
        :return: True if path is a volume, False if not
        :rtype: bool
        """
        if self.exists():
            return self.is_network_drive() or self == self.volume()
        else:
            raise PathError(f"Cannot see if non existent path " f"is a volume or not: {self}")

    def on_network_drive(self):
        """
        Check if path is on a network drive

        .. warning:: Only checks if the path starts with double slash, and may
            be somewhat unreliable. Make sure to test if it seems to work

        :return: True if path is on network drive, False if not
        :rtype: bool
        """
        return str(self).startswith("//")

    def network_drive(self):
        """
        Returns the first part of the path following the double slash

        Example::

            p = Path('//netwdrive/extensions/parts')
            p.network_drive()
                Folder('//netwdrive')

        :raises PathError: If path is not on a network drive
            (see :meth:`on_network_drive()`)
        :return: Network drive part of the path
        :rtype: Folder
        """
        if self.on_network_drive():
            return Folder("//" + self.parts()[0])
        else:
            raise PathError(f"Path is not on a network drive: {self}")

    def is_network_drive(self):
        """
        Check if path is a network drive following the same rules as
        in :meth:`on_network_drive()`

        .. note:: If on Windows, a mapped network drive will not be
            interpreted as a network drive, since the path starts with a
            drive letter

        :return: True if path is network drive, False if not
        :rtype: bool
        """
        try:
            return self.network_drive() == self
        except PathError:
            return False

    def is_folder(self):
        """
        Check if path is a folder

        :raises PathError: If path does not exist
        :return: True if path is a folder, False if not
        :rtype: bool
        """
        if self.exists():
            return os.path.isdir(self)
        else:
            raise PathError(f"Cannot determine if non existent path " f"is a folder or not: {self}")

    def is_file(self):
        """Check if path is a file

        :raises PathError: If path does not exist
        :return: True if path is a file, False if not
        :rtype: bool
        """
        if self.exists():
            return os.path.isfile(self)
        else:
            raise PathError(f"Cannot determine if non existent path " f"is a file or not: {self}")

    def size(self):
        """Return file or folder size

        .. note:: If Path is a folder, ``size()`` will return a small number,
            representing the size of the folder object, not its contents.
            For finding actual disk usage of a folder, use
            :meth:`.Folder.disk_usage()`

        :raises PathError: If path does not exist
        :returns: File or folder size
        :rtype: int
        """
        if self.exists():
            return os.stat(self).st_size
        else:
            raise PathError(f"Cannot determine size of " f"non existent path: {self}")

    def created(self):
        """
        Get created timestamp from operating system

        Wrapper for ``os.stat(<path>).st_ctime``

        .. note:: Created timestamp tends to be unreliable, especially
            when files have been moved around

        :return: Timestamp created (perhaps)
        :rtype: Zulu
        """
        return Zulu.from_epoch(os.stat(self).st_ctime)

    def modified(self):
        """
        Get modified timestamp from operating system

        Wrapper for ``os.stat(<path>).st_mtime``

        .. note:: Modified timestamp tends to be unreliable, especially
            when files have been moved around

        :returns: Timestamp modified (perhaps)
        :rtype: Zulu
        """
        return Zulu.from_epoch(os.stat(self).st_mtime)

    def parts(self):
        """
        Get list of parts in path

        Example::

            p = Path('/home/zaphod/dev/code')
            p.parts()
                ['home', 'zaphod', 'dev', 'code']

        :returns: String parts of path
        :rtype: list
        """
        parts = str(self).split(self.FOLDER_SEPARATOR)
        # Remove empty first part (if path starts with /)
        if parts[0] == "":
            parts = parts[1:]
        # Once more in case this is a network drive
        if parts[0] == "":
            parts = parts[1:]
        return parts


class Folder(Path):
    @classmethod
    def home(cls):
        """Get path to user home folder

        Wrapper for ``os.path.expanduser()``

        :return: Home folder path
        :rtype: Folder
        """
        return Folder(os.path.expanduser("~"))

    @classmethod
    def current(cls):
        """Get current folder path

        Wrapper for ``os.getcwd()``

        :return: Path to current folder
        :rtype: Folder
        """
        return cls(os.getcwd())

    def __init__(self, path, *args, **kwargs):
        super().__init__(path)
        if PIXIE:
            if self.exists():
                if self.is_file():
                    raise PixieInPipeline(f"Path is a file, " f"not a folder: {self}")

    def __repr__(self):
        return f"Folder('{self}')"

    def __truediv__(self, other):
        if isinstance(other, str) or isinstance(other, Word) or isinstance(other, Key):
            return self.append(other)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, str):
            return self.file(other)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Folder):
            str_self = str(self)
            str_other = str(other)
            if str_self.startswith(str_other):
                new_str = str_self[len(str(other)) :]
                if new_str.startswith("/"):
                    new_str = new_str[1:]
                return new_str
            else:
                raise FolderError(
                    f"Cannot subtract folder which is not part of other; "
                    f"This: {str_self};"
                    f"Other: {str_other}; "
                    f"This must start with Other"
                )
        return NotImplemented

    def create(self, error_if_exists=True):
        """Create new folder, including non existent parent folders

        :raises FolderError: If folder already exists,
            *and* ``error_if_exists=True``
        :param error_if_exists: Error flag. If True, method will raise an
            error if the folder already exists
        :type error_if_exists: bool
        :returns: True if it was created, False if not
        :rtype: bool
        """
        if not self.exists():
            os.makedirs(self)
            return True
        else:
            if error_if_exists:
                raise FolderError(f"Folder already exists: {self}")
            return False

    def touch(self):
        """
        Create folder if it does not exist, ignore otherwise
        """
        self.create(error_if_exists=False)

    def untouch(self):
        """
        Remove folder if it exists, ignore otherwise

        :raises OSError: If folder exists but is not empty
        """
        self.remove(error_if_not_exists=False)

    def parent(self):
        """Get parent folder

        :return: Parent folder
        :rtype: Folder
        """
        return Folder(os.path.dirname(str(self)))

    def append(self, *args):
        """Append strings or list of strings to current folder

        Example::

            fo = Folder.home()
            print(fo)
                '/Users/zaphod'

            fo.append('dev', 'code', 'donald')
                '/Users/zaphod/dev/code/donald'

            parts = ['dev', 'code', 'donald']
            fo.append(parts)
                '/Users/zaphod/dev/code/donald'

        :param args: Strings or list of strings
        :return: Appended folder as separate object
        :rtype: Folder
        """
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, list):
                arg = [str(x) for x in arg]
                return Folder.join(str(self), "/".join(arg))
            elif isinstance(arg, Key):
                return Folder.join(str(self), "/".join([str(x) for x in arg.words()]))
            else:
                return Folder.join(str(self), str(arg))
        else:
            return Folder.join(str(self), *args)

    def file(self, name: str):
        """
        Create file path in this folder

        :param name: File name
        :type name: str
        :return: File path in this folder
        :rtype: File
        """
        if PIXIE:
            if os.path.abspath(name) == name:
                raise PixieInPipeline(f"File name is already full path: {name}")
        return File.join(str(self), name)

    def is_empty(self):
        """Check if folder is empty

        :raise FolderError: If folder does not exist
        :return: True if empty, False if not
        :rtype: bool
        """
        if self.exists():
            return len(list(self.list())) == 0
        else:
            raise FolderError(f"Cannot check if non existent folder " f"is empty: {self}")

    # TODO: Add test for empty, with missing name
    def empty(self, name: str):
        """
        Recursively deletes all files and subfolders

        Name of folder is required to verify deleting content

        .. warning:: Be careful. Will delete  all content recursively

        :param name: Folder name as given by :meth:`.Folder.name()`.
            Required to verify deleting all contents
        :type name: str
        :raises FolderError: If folder does not exist, or if ``name`` is not
            an exact match with folder name
        """
        if self.name() != name:
            raise FolderError(f"Text of folder required to verify " f"deletion: name={self.name()}")
        if self.exists():
            for name in os.listdir(self):
                path = os.path.join(self, name)
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        else:
            raise FolderError(f"Cannot empty a non existent folder: {self}")

    def remove(self, error_if_not_exists: bool = True):
        """
        Remove folder

        :raises OSError: If folder exists but is not empty
        :raises FolderError: If folder does not exist and
            ``error_if_not_exists=True``
        :param error_if_not_exists: If True, method will raise an
            error if the folder already exists
        :type error_if_not_exists: bool
        """
        if self.exists():
            os.rmdir(str(self))
        else:
            if error_if_not_exists:
                raise FolderError(f"Cannot remove a non existent " f"folder: {self}")

    def remove_empty_folders(self):
        """
        Recursively remove empty subfolders
        """
        fo_str = str(self)
        for root, folders, files in os.walk(fo_str):
            if root != fo_str and not folders and not files:
                os.rmdir(root)

    def list(self, pattern: str = "*", recursive: bool = False):
        """
        List folder contents

        Example patterns:

            - ``'*'`` (default) Returns all files and folders except hidden
            - ``'.*`` Returns all hidden files and folders
            - ``'*.txt'`` Return all files ending with 'txt'

        .. note:: For large amounts of files and folders, use the generator
            returned by :meth:`.Folder.walk()` and handle them individually

        :raises FolderError: If folder does not exist
        :param pattern: Pattern to search for
        :param recursive: If True search will include all subfolders and files
        :return: List of :class:`.File` and/or :class:`Folder`
        :rtype: list
        """
        if not self.exists():
            raise FolderError(f"Cannot list non existent folder: {self}")

        if recursive:
            paths = glob.glob(str(self.append("**", pattern)), recursive=True)
        elif pattern is None:
            paths = os.listdir(str(self))
        else:
            paths = glob.glob(str(self.append(pattern)))

        fifo_paths: List[Union[File, Folder]] = []
        for path in paths:
            try:
                if os.path.isfile(path):
                    fifo_paths.append(File(path))
                elif os.path.isdir(path):
                    fifo_paths.append(Folder(path))
            except FileError or PathError or FolderError as e:  # type: ignore
                # TODO: Handle links and other exceptions
                self.logger.info(f"Skipping path {path} due to error: {e}")
        return fifo_paths

    def list_files(self, pattern="*", recursive=False):
        """
        List all files in this folder matching ``pattern``

        Uses :meth:`.Folder.list()` and then filters out all :class:`.File`
        objects and returns the result

        .. note:: For large amounts of files, use the generator
            returned by :meth:`.Folder.files()` and handle them individually

        :raises FolderError: If folder does not exist
        :param pattern: Pattern to search for
        :param recursive: If True search will include all subfolders and files
        :return: List of :class:`.File` objects
        :rtype: list
        """
        paths = self.list(pattern=pattern, recursive=recursive)
        return [x for x in paths if isinstance(x, File)]

    def list_folders(self, pattern="*", recursive=False):
        """
        List all folders in this folder matching ``pattern``

        Uses :meth:`.Folder.list()` and then filters out all :class:`.Folder`
        objects and returns the result

        .. note:: For large amounts of folders, use the generator
            returned by :meth:`.Folder.folders()` and handle them individually

        :raises FolderError: If folder does not exist
        :param pattern: Pattern to search for
        :param recursive: If True search will include all subfolders and files
        :return: List of :class:`.Folder` objects
        :rtype: list
        """
        paths = self.list(pattern=pattern, recursive=recursive)
        return [x for x in paths if isinstance(x, Folder)]

    def walk(self, include_files: bool = True, include_folders: bool = True):
        """
        Generator listing all files and folders in this folder recursively

        :return: Generator object returning :class:`File` or :class:`Folder`
            for each iteration
        :rtype: generator
        """
        for root, fos, fis in os.walk(str(self)):
            if include_folders:
                for fo in (Folder.join(root, x) for x in fos):
                    if fo.exists():
                        yield fo
            if include_files:
                for fi in (File.join(root, x) for x in fis):
                    if fi.exists():
                        yield fi

    def files(self):
        """
        Generator listing all files in this folder recursively

        Print all files larger than 1 kB in home folder and all subfolders::

            fo = Folder.home()
            for fi in fo.files():
                if fi.size() > 1000:
                    print(fi)

        :return: Generator object returning :class:`File` for each iteration
        :rtype: generator
        """
        return self.walk(include_files=True, include_folders=False)

    def folders(self):
        """
        Generator listing all folders in this folder recursively

        :return: Generator object returning :class:`Folder` for each iteration
        :rtype: generator
        """
        return self.walk(include_files=False, include_folders=True)

    def count(self, include_files: bool = True, include_folders: bool = True):
        """
        Count number of files and/or folders recursively

        .. note:: Links will also be included

        :param include_files: Include files in count
        :type include_files: bool
        :param include_folders: Include folders in count
        :type include_folders: bool
        :return: Number of files and/or folders in folder
        :rtype: int
        """
        count = 0
        for root, fos, fis in os.walk(str(self)):
            if include_folders:
                count += len(fos)
            if include_files:
                count += len(fis)
        return count

    def count_files(self):
        """
        Count number of files recursively

        .. note:: Links will also be included

        :return: Number of files in folder
        :rtype: int
        """
        return self.count(include_files=True, include_folders=False)

    def count_folders(self):
        """
        Count number of folders recursively

        .. note:: Links will also be included

        :return: Number of folders in folder
        :rtype: int
        """
        return self.count(include_files=False, include_folders=True)

    def disk_usage(self, include_folders: bool = False, include_files: bool = True):
        """
        Recursively determines disk usage of all contents in folder

        :param include_folders: If True, all folder sizes will be included in
            total, but this is only the folder object and hence a small number.
            Default is therefore False
        :param include_files: If True, all file sizes are included in total.
            Default is obviously True
        :raises FolderError: If folder does not exist
        :return: Disk usage of folder content
        :rtype: int
        """
        if not self.exists():
            raise FolderError(f"Cannot determine disk usage of " f"non existent folder: {self}")
        size = 0
        for root, fos, fis in os.walk(str(self)):
            if include_folders:
                for fo in fos:
                    try:
                        size += os.stat(os.path.join(root, fo)).st_size
                    except FileNotFoundError:
                        pass
            if include_files:
                for fi in fis:
                    try:
                        size += os.stat(os.path.join(root, fi)).st_size
                    except FileNotFoundError:
                        pass
        return size

    def print(self, count: bool = False, disk_usage: bool = False):
        """
        Print folder content

        :param count: Include count for each subfolder
        :type count: bool
        :param disk_usage: Include disk usage for each subfolder, and size
            for each file
        :type disk_usage: bool
        """
        paths = self.list()
        for path in paths:
            if not path.exists():
                print(f"{path.name()} [link or deleted]")
            else:
                if path.is_folder():
                    print(f"{path.name()} [Folder]")
                    if count or disk_usage:
                        fo = Folder(str(path))
                        if count:
                            nfo = fo.count_folders()
                            print(f"\tSubfolder count: {nfo}")
                            nfi = fo.count_files()
                            print(f"\tFile count: {nfi}")
                        if disk_usage:
                            du = fo.disk_usage()
                            dustr = Math.bytes_to_human(du)
                            print(f"\tDisk usage: {dustr}")
                elif path.is_file():
                    print(f"{path.name()} [File]")
                    if disk_usage:
                        fi = File(str(path))
                        size = Math.bytes_to_human(fi.size())
                        print(f"\tSize: {size}")
                else:
                    print(f"{path.name()} [unknown]")

    # def print(self,
    #           indent: int = 2,
    #           include_files: bool = True,
    #           include_folders: bool = True):
    #     """
    #     :param indent:
    #     :param include_files:
    #     :param include_folders:
    #     :return:
    #     """
    #     # TODO: Redo with sequential walkthrough, and max_depth
    #     fo_str = str(self)
    #     for path in self.walk(include_files=include_files,
    #                           include_folders=include_folders):
    #         level = str(path).replace(fo_str, '').count('/')
    #         path_indent = ' ' * indent * level
    #         path_tag = ''
    #         if path.is_folder():
    #             path_tag = '/'
    #         print(f'{path_indent}{path.name()}{path_tag}')


# class FileElements(Doc):
#     __pixie = Config.PIXIE_IN_PIPELINE
#
#
#
#     COMPRESSED_ENDSWITH = EXTENSION_SEPARATOR + COMPRESSED_EXTENSION
#     ENCRYPTED_ENDSWITH = EXTENSION_SEPARATOR + ENCRYPTED_EXTENSION
#     COMPRESSED_AND_ENCRYPTED_ENDSWITH = \
#         EXTENSION_SEPARATOR + COMPRESSED_EXTENSION + ENCRYPTED_ENDSWITH
#
#     def __init__(self,
#                  stub: str,
#                  extension: str,
#                  is_hidden: bool = False,
#                  is_compressed: bool = False,
#                  is_encrypted: bool = False):
#         """
#         Create file name from stub and attributes
#
#         :param stub: File stub, barring extensions and hidden startswith
#         :param extension: File extension
#         :param is_hidden: True tags file name as hidden
#         :param is_compressed: True tags file name as compressed, adding the
#             necessary extra extension
#         :param is_encrypted:
#         :return:
#         """
#         super().__init__()
#         if self.__pixie:
#             if stub.startswith(self.HIDDEN_STARTSWITH):
#                 raise FileError(f'Stub cannot start with the hidden flag. '
#                                 f'Keep stub clean, and set is_hidden=True')
#             if self.EXTENSION_SEPARATOR in stub:
#                 raise FileError(f'Cannot add stub with extension '
#                                 f'separator in it: {stub}. '
#                                 f'Need a clean string for this')
#             if self.EXTENSION_SEPARATOR in extension:
#                 raise FileError(f'Cannot add extension with extension '
#                                 f'separator in it: {extension}. '
#                                 f'Need a clean string for this')
#         self.stub = stub
#         self.extension = extension
#         self.is_hidden = is_hidden
#         self.is_compressed = is_compressed
#         self.is_encrypted = is_encrypted
#         if self.__pixie:
#             if self.EXTENSION_SEPARATOR in extension:
#                 raise PixieInPipeline(f'There should not be a separator in '
#                                       f'an extension: {extension}')
#
#         self.__name = None

# def __str__(self):
#     if not self.__name:
#         names = [self.stub, self.extension]
#         if self.is_compressed:
#             names += [self.COMPRESSED_EXTENSION]
#         if self.is_encrypted:
#             names += [self.ENCRYPTED_EXTENSION]
#         name = self.EXTENSION_SEPARATOR.join(names)
#         if self.is_hidden:
#             name = self.HIDDEN_STARTSWITH + name
#         self.__name = name
#     return self.__name

# def parts(self):
#     parts = [self.stub,
#              self.extension]
#     if self.is_compressed:
#         parts += self.COMPRESSED_EXTENSION
#     if self.is_encrypted:
#         parts += self.ENCRYPTED_EXTENSION
#     return parts
#
#
#     return dict(stub=stub,
#                 extension=extension,
#                 extensions=extensions,
#                 is_hidden=is_hidden,
#                 is_compressed=is_compressed,
#                 is_encrypted=is_encrypted)

# def from_name(self, name):
#     di = self.name_to_dict(name):
#     if not di['extensions']:
#
# def __repr__(self):
#     kwargs = [f'\'{self.stub}\'',
#               f'\'{self.extension}\'']
#     if self.is_hidden:
#         kwargs += f'is_hidden={self.is_hidden}'
#     if self.is_compressed:
#         kwargs += f'is_compressed={self.is_compressed}'
#     if self.is_encrypted:
#         kwargs += f'is_encrypted={self.is_encrypted}'
#     kwargs = ', '.join(kwargs)
#     return f'FileElements({kwargs})'


class File(Path):
    """
    Convenience class for file handling

    Create a file path in current folder::

        fi = File('my_file.txt')
        fi
            File('/home/zaphod/current/my_file.txt')

    Create a file path in home folder::

        fi = File.home('my_file.txt')
        fi
            File('/home/zaphod/my_file.txt')

    Create a file path in some folder::

        fo = Folder.home().append('some/folder')
        fo
            Folder('/home/zaphod/some/folder')
        fi = fo.file('my_file.txt')
        fi
            File('/home/zaphod/some/folder/my_file.txt')

    Create and read a file::

        fi = File('my_file.txt')
        fi.write('Hello world')
        fi.read()
            'Hello world'
        fi.size()
            11

    Compress and encrypt::

        fi.compress()
        fi.name()
            'my_file.txt.gz'
        fi.read()
            'Hello world'

        crypt_key = Crypt.generate_key()
        crypt_key
            b'aLQYOIxZOLllYThEKoXTH_eqTQGEnXm9CUl2glq3a2M='
        fi.encrypt(crypt_key)
        fi.name()
            'my_file.txt.gz.aes'
        fi.read(crypt_key=crypt_key)
            'Hello world'

    Create an encrypted file, and write to it::

        ff = File('my_special_file.txt.aes')
        ff.write('Hello there', password='123')
        ff.read(password='123')
            'Hello there'

        f = open(ff)
        f.read()
            'gAAAAABe0BYqPPYfzha3AKNyQCorg4TT8DcJ4XxtYhMs7ksx22GiVC03WcrMTnvJLjTLNYCz_N6OCmSVwk29Q9hoQ-UkN0Sbbg=='
        f.close()

    .. note:: Using the ``password`` parameter, builds an encryption key by
        combining it with the builtin (i.e. hard coded) class salt.
        For proper security, generate your
        own salt with :meth:`.Crypt.salt()`. Store this salt appropriately,
        then use :meth:`.Crypt.key_from_password()` to generate a crypt_key

    .. warning:: \'123\' is not a real password

    """

    _salt = b"O89ogfFYLGUts3BM1dat4vcQ"

    logger = logging.getLogger(__name__)

    #: Files with this extension will compress text before writing to file
    #: and decompress after reading
    COMPRESSED_EXTENSION = COMPRESSED_EXTENSION

    #: Files with this extension will encrypt before writing to file, and
    #: decrypt after reading. The read/write methods therefore require a
    #: crypt_key
    ENCRYPTED_EXTENSION = ENCRYPTED_EXTENSION

    JSON_EXTENSION = "json"
    YAML_EXTENSION = "yaml"

    # #: Extensions reserved for compression and encryption
    # RESERVED_EXTENSIONS = [COMPRESSED_EXTENSION,
    #                        ENCRYPTED_EXTENSION]

    #: File names starting with this character will be tagged as hidden
    HIDDEN_STARTSWITH = "."

    #: Extension separator. Period
    EXTENSION_SEPARATOR = "."

    # TODO: Add binary flag based on extension (all other than text is binary..)
    # TODO: Facilitate child classes with custom read/write needs

    @classmethod
    def make(
        cls,
        folder,
        stub: str,
        extension: str,
        is_hidden: bool = False,
        is_compressed: bool = False,
        is_encrypted: bool = False,
    ):
        """
        Create a file path following proper file name structure

        :param folder: Containing folder
        :type folder: Folder
        :param stub: File stub
        :type stub: str
        :param extension: File extension added after file stub
        :type extension: str
        :param is_hidden: Whether file is hidden or not. True will add
             :data:`HIDDEN_STARTSWITH` to beginning of filename
        :type is_hidden: bool
        :param is_compressed: True will add the :data:`COMPRESSED_EXTENSION`
            after the regular extension
        :type is_compressed: bool
        :param is_encrypted: True will add the :data:`ENCRYPTED_EXTENSION`
            after the regular extension and possible compressed extension
        :type is_encrypted: bool
        :rtype: File
        """
        folder = Folder.glass(folder)
        names = [stub, extension]
        if is_compressed:
            names += [cls.COMPRESSED_EXTENSION]
        if is_encrypted:
            names += [cls.ENCRYPTED_EXTENSION]
        name = cls.EXTENSION_SEPARATOR.join(names)
        if is_hidden:
            name = cls.HIDDEN_STARTSWITH + name

        return cls.join(folder, name)

    @classmethod
    def home(cls, file_name: str):
        """
        Create a file path in home folder

        :param file_name: File name
        :type file_name: str
        :rtype: File
        """
        return cls.join(Folder.home(), file_name)

    @classmethod
    def _crypt_key(cls, crypt_key: Optional[bytes] = None, password: Optional[str] = None):
        if crypt_key is None and password is None:
            raise FileError("crypt_key or password missing")
        elif crypt_key is not None and password is not None:
            raise FileError("Use either crypt_key or password.")
        if crypt_key is not None:
            return crypt_key
        elif password is not None:
            return Crypt.key_from_password(cls._salt, password)
        else:
            raise FileError("FATAL: This should be unreachable")

    def __init__(self, path: str, *args, **kwargs):
        super().__init__(path)
        if PIXIE:
            if self.exists():
                if self.is_volume():
                    raise PixieInPipeline(f"Path is volume, not file: {path}")
                elif self.is_folder():
                    raise PixieInPipeline(f"Path is existing folder, " f"not file: {path}")
        # Lazy parsing of file name to avoid unnecessary processing
        self.__name_is_parsed = False
        self.__parts = None
        self.__stub: Optional[str] = None
        self.__extension: Optional[str] = None
        self.__extensions: List[str] = []
        self.__hidden: Optional[bool] = None
        self.__compressed: Optional[bool] = None
        self.__encrypted: Optional[bool] = None

    def __repr__(self):
        return f"File('{self}')"

    def _rename(self, new_path: str):
        super()._rename(new_path)
        self.__name_is_parsed = False

    def _parse_name(self):
        if not self.__name_is_parsed:
            name = self.name()
            self.__hidden = name.startswith(self.HIDDEN_STARTSWITH)
            if self.__hidden:
                name = name[1:]
            parts = name.split(self.EXTENSION_SEPARATOR)
            while not parts[0]:
                parts = parts[1:]
            self.__parts = parts.copy()
            self.__stub = parts[0]
            parts = parts[1:]
            self.__extension = None
            self.__extensions = parts
            self.__compressed = False
            self.__encrypted = False
            if parts and parts[-1] == self.ENCRYPTED_EXTENSION:
                self.__encrypted = True
                parts = parts[:-1]

            if parts and parts[-1] == self.COMPRESSED_EXTENSION:
                self.__compressed = True
                parts = parts[:-1]

            if len(parts) == 1:
                self.__extension = self.__extensions[0]
            self.__name_is_parsed = True

    def parts(self):
        """
        Get file parts, i.e. those separated by period

        :return: list
        """
        self._parse_name()
        return self.__parts

    def touch(self):
        """
        Create empty file if it does not exist already
        """
        self.folder().touch()
        Path_(self).touch()

    def untouch(self, ignore_if_not_empty=False):
        """
        Delete file if it exists, and is empty

        :param ignore_if_not_empty: If True, no exception is raised if file
            is not empty and thus cannot be deleted with untouch
        :return:
        """
        if self.exists():
            if self.size() == 0:
                self.delete()
            else:
                if not ignore_if_not_empty:
                    raise FileError(
                        f"Cannot untouch file "
                        f"that is not empty: {self}; "
                        f"Use delete() to delete a non-empty file"
                    )

    def extensions(self):
        """
        Get file extensions as a list of strings

        :return: List of file extensions
        :rtype: list
        """
        self._parse_name()
        return self.__extensions

    def is_hidden(self):
        """
        Check if file is hidden, i.e. starts with :data:`HIDDEN_STARTSWITH`

        :return: True if hidden, False if not
        :rtype: bool
        """
        self._parse_name()
        return self.__hidden

    def is_compressed(self):
        """
        Check if file is compressed, i.e. has :data:`COMPRESSED_EXTENSION`

        :return: True if compressed, False if not
        :rtype: bool
        """
        self._parse_name()
        return self.__compressed

    def is_encrypted(self):
        """
        Check if file is encrypted, i.e. has :data:`ENCRYPTED_EXTENSION`

        :return: True if encrypted, False if not
        :rtype: bool
        """
        self._parse_name()
        return self.__encrypted

    def stub(self):
        """
        Get file stub, i.e. the part of the file name bar extensions and
        :data:`HIDDEN_STARTSWITH`

        Example::

            fi = File('.hidden_with_extensions.json.gz')
            fi.stub()
                'hidden_with_extensions'

        :return: File stub
        :rtype: str
        """
        self._parse_name()
        return self.__stub

    def extension(self):
        """
        Get file extension, i.e. the extension which is not reserved.
        A file is only supposed to have one extension that does not indicate
        either compression or encryption.

        :raise FileError: If file has more than one extension barring
            :data:`COMPRESSED_EXTENSION` and :data:`ENCRYPTED_EXTENSION`
        :return: File extension
        :rtype: str
        """
        self._parse_name()
        return self.__extension

    def md5_checksum(self, usedforsecurity=False):
        """
        Get MD5 Checksum for the file

        :raise FileError: If file does not exist
        :return: MD5 Checksum
        :rtype: str
        """
        if not self.exists():
            raise FileError(f"Cannot make checksum " f"if file does not exist: {self}")
        md5 = hashlib.md5(usedforsecurity=usedforsecurity)
        with open(self, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def new(self, name):
        """
        Create a new file path in same folder as current file

        :param name: New file name
        :rtype: File
        """
        return self.folder().file(name)

    def delete(self, missing_ok: bool = False):
        """
        Delete file

        :raise FileError: If file is missing, and ``missing_ok=False``
        :param missing_ok: Indicate if an exception should be raised if the
            file is missing. If True, an exception will not be raised
        :type missing_ok: bool
        """
        if self.exists():
            self.logger.debug(f"Delete file: {self}")
            os.unlink(self)
        elif not missing_ok:
            raise FileError(f"Tried to delete file " f"that doesn't exist: {self}")

    def delete_if_exists(self):
        """
        Delete file if exists
        """
        self.delete(missing_ok=True)

    def write(self, data, mode="w", crypt_key: Optional[bytes] = None, password: Optional[str] = None, **kwargs):
        """
        Write data to file

        For encryption, use either ``crypt_key`` or ``password``. None or both
        will raise an exception. Encryption requires the file name to end with
        :data:`ENCRYPTED_EXTENSION`

        :raise FileError: If using ``crypt_key`` or ``password``, and the
            file does not have encrypted extension
        :param data: Data to write
        :type data: str or bytes
        :param mode: Write mode
        :type mode: str
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        """
        if PIXIE and (crypt_key or password) and not self.is_encrypted():
            raise PixieInPipeline(
                f"File does not have crypt extension "
                f"({self.ENCRYPTED_EXTENSION}), "
                f"but a crypt_key "
                f"or password was sent as input to write."
            )

        if self.is_encrypted():
            crypt_key = self._crypt_key(crypt_key=crypt_key, password=password)

        self.folder().touch()
        if self.is_compressed():
            if self.is_encrypted():
                self._write_compressed_and_encrypted(data, crypt_key=crypt_key)
            else:
                self._write_compressed(data)
        elif self.is_encrypted():
            self._write_encrypted(data, crypt_key=crypt_key)
        else:
            self._write(data, mode=mode)

    def write_json(
        self,
        data: dict,
        human: bool = False,
        crypt_key: Optional[bytes] = None,
        password: Optional[str] = None,
        **kwargs,
    ):
        """
        Write dictionary to JSON file

        Extends :meth:`.JSON.dumps()` with :meth:`.File.write()`

        For encryption, use either ``crypt_key`` or ``password``. None or both
        will raise an exception. Encryption requires the file name to end with
        :data:`ENCRYPTED_EXTENSION`

        :raise FileError: If using ``crypt_key`` or ``password``, and the
            file does not have encrypted extension
        :param data: Data to write
        :type data: str or bytes
        :param human: If True, write JSON as human readable
        :type human: bool
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        """
        data = JSON.dumps(data, human=human)
        self.write(data, mode="w", crypt_key=crypt_key, password=password)

    def write_yaml(self, data: dict, crypt_key: Optional[bytes] = None, password: Optional[str] = None, **kwargs):
        """
        Write dictionary to YAML file

        Extends :meth:`.YAML.dumps()` with :meth:`.File.write()`

        For encryption, use either ``crypt_key`` or ``password``. None or both
        will raise an exception. Encryption requires the file name to end with
        :data:`ENCRYPTED_EXTENSION`

        :raise FileError: If using ``crypt_key`` or ``password``, and the
            file does not have encrypted extension
        :param data: Data to write
        :type data: str or bytes
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        """
        data = YAML.dumps(data)
        self.write(data, mode="w", crypt_key=crypt_key, password=password)

    def _write(self, data, mode="w"):
        with open(self, mode=mode) as f:
            f.write(data)

    def _write_compressed(self, content):
        if not isinstance(content, bytes):
            content = content.encode()
        with gzip.open(self, mode="wb") as f:
            f.write(content)

    def _write_encrypted(self, content, crypt_key=None):
        if not isinstance(content, bytes):
            content = content.encode()
        with open(self, mode="wb") as f:
            f.write(Crypt.encrypt(content, crypt_key))

    def _write_compressed_and_encrypted(self, content, crypt_key=None):
        if not isinstance(content, bytes):
            content = content.encode()
        with gzip.open(self, mode="wb") as f:
            f.write(Crypt.encrypt(content, crypt_key))

    def open(self, mode="r"):
        """
        Open file

        Returns a file handle by extending builtin ``open()``

        Intended use::

            fi = File("look_at_me.txt")
            with fi.open() as f:
                print(f.read())  # Do something more elaborate than this

            # This would also work (making this method rather useless)
            with open(fi) as f:
                print(f.read())

            # Better solution for this simple example
            print(fi.read())

        :param mode: File open mode
        :return: File handle
        """
        return open(self, mode=mode)

    def _is_binary(self, mode):
        return "b" in mode

    def readlines(self, num_lines=1):
        """
        Read lines in file

        Does not work with encrypted files

        Intended use is reading the header of a file

        :param num_lines: Number of lines to read. Default is 1
        :return: First line as a string if ``num_lines=1``, or a list of
            strings for each line
        :rtype: str or list
        """
        if PIXIE and self.is_encrypted():
            raise PixieInPipeline("Cannot read lines in encrypted file")
        if self.is_compressed():
            return self._readlines_compressed(num_lines=num_lines)
        else:
            return self._readlines(num_lines=num_lines)

    def read(self, mode="r", crypt_key: Optional[bytes] = None, password: Optional[str] = None, *args, **kwargs):
        """
        Read file

        If file is encrypted, use either ``crypt_key`` or ``password``.
        None or both will raise an exception. Encryption requires the file
        name to end with :data:`ENCRYPTED_EXTENSION`

        :raises FileError: If trying to decrypt a file without
            :data:`ENCRYPTED_EXTENSION`
        :param mode: Read mode
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        :return: Data as string or bytes depending on read mode
        :rtype: str or bytes
        """
        if not self.exists():
            raise FileError(f"Cannot read from file " f"that does not exist: {self}")
        elif PIXIE and (crypt_key or password) and not self.is_encrypted():
            raise PixieInPipeline(
                f"File does not have crypt extension "
                f"({self.ENCRYPTED_EXTENSION}), "
                f"but a crypt_key "
                f"or password was sent as input to write."
            )
        if self.is_encrypted():
            crypt_key = self._crypt_key(crypt_key=crypt_key, password=password)

        if self.is_compressed():
            if self.is_encrypted():
                data = self._read_compressed_and_encrypted(crypt_key)
                if "b" not in mode:
                    data = data.decode()
            else:
                data = self._read_compressed(mode=mode)
                if "b" not in mode:
                    data = data.decode()
        else:
            if self.is_encrypted():
                data = self._read_encrypted(crypt_key=crypt_key)
                if "b" not in mode:
                    data = data.decode()
            else:
                data = self._read(mode=mode)

        return data

    def read_json(self, crypt_key: Optional[bytes] = None, password: Optional[str] = None, **kwargs):
        """
        Read json file

        Extends :meth:`.File.read()` with :meth:`.JSON.loads()`

        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        :return: Dictionary of JSON content
        :rtype: dict
        """
        data = self.read(mode="r", crypt_key=crypt_key, password=password)
        return JSON.loads(data)

    def read_yaml(self, crypt_key: Optional[bytes] = None, password: Optional[str] = None, **kwargs):
        """
        Read json file

        Extends :meth:`.File.read()` with :meth:`.YAML.loads()`

        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        :return: Dictionary of YAML content
        :rtype: dict
        """
        data = self.read(mode="r", crypt_key=crypt_key, password=password)
        return YAML.loads(data)

    def _read(self, mode="r"):
        with open(self, mode=mode) as f:
            return f.read()

    def _readlines(self, num_lines=1):
        with open(self) as f:
            content = []
            for n in range(num_lines):
                content.append(f.readline().strip())
            if len(content) == 1:
                return content[0]
        return content

    def _read_compressed(self, mode="rb"):
        with gzip.open(self, mode=mode) as f:
            return f.read()

    def _readlines_compressed(self, num_lines=1):
        with gzip.open(self, mode="rt") as f:
            content = []
            for n in range(num_lines):
                content.append(f.readline().strip())
        if not isinstance(content, str):
            if isinstance(content, list):
                for n in range(len(content)):
                    if isinstance(content[n], bytes):
                        content[n] = content[n].decode()  # type: ignore
            elif isinstance(content, bytes):
                content = content.decode()

        if len(content) == 1:
            return content[0]
        return content

    def _read_encrypted(self, crypt_key):
        data = self._read(mode="rb")
        decrypted = Crypt.decrypt(data, crypt_key)
        return decrypted

    def _read_compressed_and_encrypted(self, crypt_key):
        with gzip.open(self, mode="rb") as f:
            data = f.read()
        decrypted = Crypt.decrypt(data, crypt_key)
        return decrypted

    # def make_new_name(self,
    #                   stub,
    #                   extension,
    #                   is_hidden=False,
    #                   is_compressed=False,
    #                   is_encrypted=False):
    #     pass

    def rename(self, new_name: str):
        """
        Rename file

        :param new_name: New file name, including extension
        :type new_name: str
        :return: A file path with the new file name
        :rtype: File
        """
        new_path = str(self.join(self.folder(), new_name))
        os.rename(self, new_path)
        self._rename(new_path)

    def folder(self):
        """
        Get the folder containing the file

        :return: Folder containing the file
        :rtype: Folder
        """
        return Folder(os.path.dirname(self))

    def move(self, new_folder: Folder, new_name=None, overwrite: bool = False):
        """
        Move file to a new folder, and with an optional new name

        :param new_folder: New folder
        :type new_folder: Folder
        :param new_name: New file name (optional). If missing, the file will
            keep the same name
        :return: Moved file
        :rtype: File
        """
        if not self.exists():
            raise FileError(f"Cannot move non existent file: {self}")
        if PIXIE and not overwrite:
            if self.folder() == new_folder:
                if new_name and new_name == self.name():
                    raise FileError(f"Cannot move a file to the same name: {self}")
        new_folder.touch()
        if new_name:
            new_file = File.join(new_folder, new_name)
        else:
            new_file = File.join(new_folder, self.name())
        if not overwrite and new_file.exists():
            raise FileError("Target file already exists. Use overwrite=True to allow overwrite")
        shutil.move(self, new_file)
        self._rename(str(new_file))

    def copy(self, new_folder, new_name: Optional[str] = None, overwrite: bool = False):
        """
        Copy file to a new folder, and optionally give it a new name

        :param overwrite: Set True to overwrite destination file if it exists
        :type overwrite: bool
        :param new_folder: New folder
        :type new_folder: Folder or str
        :param new_name: New file name (optional). If missing, the file will
            keep the same name
        :type new_name: str
        :return: Copied file
        :rtype: File
        """
        new_folder = Folder.glass(new_folder)
        if self.folder() == new_folder:
            raise FileError(f"Cannot copy a file " f"to the same folder: {new_folder}")
        new_folder.touch()
        if new_name:
            new_file = File.join(new_folder, new_name)
        else:
            new_file = File.join(new_folder, self.name())
        if not overwrite and new_file.exists():
            raise FileError(f"Target file exists: {new_file}; " f"Use overwrite=True to allow overwrite")
        shutil.copyfile(self, new_file)
        return new_file

    def compress(self, delete_original: bool = True):
        """
        Compress file

        :param delete_original: If True, original file will be deleted after
            compression (default)
        :type delete_original: bool
        """
        if self.is_compressed():
            raise FileError(f"File already compressed: {self}")
        if self.is_encrypted():
            raise FileError(f"Cannot compress encrypted file: {self}. " f"Decrypt file first")

        self.logger.debug(f"Compress file: {self}")
        old_size = self.size()
        new_file = File(f"{self}.gz")
        if new_file.exists():
            self.logger.warning(f"Overwrite existing gz-file: {new_file}")
        with open(self, "rb") as f_in:
            with gzip.open(str(new_file), "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        if delete_original:
            self.delete()
        compression_percent = 100 * (old_size - new_file.size()) / old_size
        self.logger.debug(f"Compressed with compression " f"{compression_percent:.2f} %")
        self._rename(str(new_file))

    def decompress(self, delete_original: bool = True, replace_if_exists: bool = True):
        """
        Decompress file

        :param delete_original: If True, the original compressed file will be
            deleted after decompression
        :type delete_original: bool
        :param replace_if_exists: If True, the decompressed file will replace
            any already existing file with the same name
        :type replace_if_exists: bool
        """
        if not self.is_compressed():
            raise FileError(f"File is not compressed: {self}")
        if self.is_encrypted():
            raise FileError(f"Cannot decompress encrypted file: {self}. " f"Decrypt file first.")
        self.logger.debug(f"Decompress file: {self}")
        new_file = File(str(self).replace("." + self.COMPRESSED_EXTENSION, ""))
        if new_file.exists():
            if replace_if_exists:
                self.logger.debug(f"Overwrite existing file: {new_file}")
            else:
                raise FileError(f"File already exists: '{new_file}'. " f"Use replace_if_exists=True to ignore.")
        with gzip.open(self, "rb") as f_in:
            with open(new_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        if delete_original:
            self.delete()
        new_file = File.glass(new_file)
        # new_file.compression_percent = None
        self._rename(str(new_file))

    def encrypt(self, crypt_key: bytes, delete_original: bool = True):
        """
        Encrypt file

        :raise FileError: If file is already encrypted or if crypt_key is
            missing
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param delete_original: If True, the original unencrypted file will
            be deleted after encryption
        :type delete_original: bool
        """
        if self.is_encrypted():
            raise FileError(f"File is already encrypted: {self}")
        self.logger.debug(f"Encrypt file: {self}")
        encrypted_file = File(f"{self}.{self.ENCRYPTED_EXTENSION}")
        data = self._read(mode="rb")
        encrypted = Crypt.encrypt(data, crypt_key)
        encrypted_file._write(encrypted, mode="wb")
        if delete_original:
            self.delete()
        self._rename(str(encrypted_file))

    def decrypt(self, crypt_key: bytes, delete_original: bool = True):
        """
        Decrypt file

        :raise FileError: If file is not encrypted or if crypt_key is missing
        :param crypt_key: Encryption key
        :type crypt_key: bool
        :param delete_original: If True, the original encrypted file will
            be deleted after decryption
        :type delete_original: bool
        """
        if not self.is_encrypted():
            raise FileError(f"File is not encrypted: {self}")

        self.logger.debug(f"Decrypt file: {self}")
        decrypted_file = File(str(self).replace("." + self.ENCRYPTED_EXTENSION, ""))
        data = self._read(mode="rb")
        decrypted = Crypt.decrypt(data, crypt_key)
        decrypted_file._write(decrypted, mode="wb")
        if delete_original:
            self.delete()
        self._rename(str(decrypted_file))


class Archive:
    """
    Zip file to gz conversion

    """

    # TODO: Add gz to zip
    # TODO: Add handling of multiple files and folders in archive

    @classmethod
    def is_zip(cls, file: File):
        """
        Check if input file is zip archive

        :param file: Input file
        :return: True if extension is 'zip', false if not
        :rtype: bool
        """
        extensions = file.extensions()
        return len(extensions) > 0 and extensions[-1] == "zip"

    @classmethod
    def zip_to_gz(cls, file: File, delete_source_file: bool = True):
        """
        Convert zip file to gzip compressed file

        :param file: Input zip archive
        :param delete_source_file: Delete source file if True
        """

        if not cls.is_zip(file):
            raise ArchiveError(f"File is not zip-file: {file}")

        with zipfile.ZipFile(file, "r") as zr:
            file_info_li = zr.filelist
            if len(file_info_li) > 1:
                raise ArchiveError(f"Multiple files in archive: {file}")
            elif len(file_info_li) == 0:
                raise ArchiveError(f"No files in archive: {file}")
            file_info = file_info_li[0]
            file_name = file_info.filename
            if "/" in file_name:
                file_name = file_name.split("/")[-1]
            if "\\" in file_name:
                file_name = file_name.split("\\")[-1]
            gz_file = File.join(file.folder(), file_name + ".gz")
            with zr.open(file_info, "r") as zf:
                with gzip.open(gz_file, "w") as gf:
                    shutil.copyfileobj(zf, gf)

        if delete_source_file:
            file.delete()

        return gz_file


HOME = Folder.glass(HOME)
