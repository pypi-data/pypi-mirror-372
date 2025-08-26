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

from mjooln import *


class Store:
    """
    .. danger:: Experimental class. May change without notice and suddenly disappear

    Facilitates storage of config files and encryption keys using :class:`Key` as
    a replacement for file name

    """

    _folder = HOME / "store"
    _extension = "txt"
    _is_compressed = False
    _is_encrypted = False
    _type = None

    @classmethod
    def file(cls, key):
        key = Key.glass(key)
        type = cls._type if cls._type is not None else key.first()
        return File.make(
            folder=cls._folder.append(type),
            stub=key.seed(),
            extension=cls._extension,
            is_compressed=cls._is_compressed,
            is_encrypted=cls._is_encrypted,
        )

    @classmethod
    def exists(cls, key):
        return cls.file(key).exists()

    @classmethod
    def get(cls, key, crypt_key=None, password=None):
        file = cls.file(key)
        return file.read(mode="rt", crypt_key=crypt_key, password=password)

    @classmethod
    def put(cls, key, data, crypt_key=None, password=None):
        file = cls.file(key)
        file.write(data=data, mode="wt", crypt_key=crypt_key, password=password)


class DocStore(Store):
    _folder = Store._folder.append("doc")
    _extension = "json"

    @classmethod
    def get(cls, key, crypt_key=None, password=None):
        file = cls.file(key)
        return file.read_json(crypt_key=crypt_key, password=password)

    @classmethod
    def put(cls, key, data, crypt_key=None, password=None):
        file = cls.file(key)
        file.write_json(data=data, password=password, crypt_key=crypt_key)


class ConfigStore(Store):
    _folder = Store._folder.append("config")
    _extension = "yaml"

    @classmethod
    def get(cls, key, crypt_key=None, password=None):
        file = cls.file(key)
        return file.read_yaml(crypt_key=crypt_key, password=password)

    @classmethod
    def put(cls, key, data, crypt_key=None, password=None):
        file = cls.file(key)
        file.write_yaml(data=data, password=password, crypt_key=crypt_key)


class CryptKeyStore(Store):
    _folder = Store._folder.append("crypt_key")
    _extension = "txt"
    _is_encrypted = True
    _is_compressed = True
