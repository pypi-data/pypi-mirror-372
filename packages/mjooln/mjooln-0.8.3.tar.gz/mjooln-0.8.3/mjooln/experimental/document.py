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


class Document(Doc):
    """
    .. danger:: Experimental class. May change without notice and suddenly disappear

    Class with functionality to store attributes in file as JSON or YAML

    Has an ``atom`` attribute as default, as well as private
    created and modified attributes stored in file due
    to unreliable file system handling of these
    """

    ALLOWED_EXTENSIONS = ["json", "yaml"]

    @classmethod
    def load(cls, file, crypt_key: bytes = None, password: str = None):
        """
        Load Document file

        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use builtin salt)
        :type password: str
        :raises DocumentError: If extension is not valid. Must be \'json\' or
            \'yaml\'
        :param file: Document file
        :return: Document instance based on file contents
        :rtype: Document
        """
        file = File.glass(file)
        doc_str = file.read(crypt_key=crypt_key, password=password)
        if file.extension() == File.JSON_EXTENSION:
            doc = JSON.loads(doc_str)
        elif file.extension() == File.YAML_EXTENSION:
            doc = YAML.loads(doc_str)
        else:
            raise DocumentError(f"Invalid extension: {file.extension()}")
        doc["file"] = file
        doc["crypt_key"] = crypt_key
        doc["password"] = password
        return cls.from_doc(doc)

    def __init__(self, file, atom=None, crypt_key=None, password=None, **kwargs):
        self.__file = File.glass(file)
        self.__crypt_key = crypt_key
        self.__password = password
        self.__created = None
        self.__modified = None
        self.atom = Atom.glass(atom) if atom else None
        if PIXIE:
            if self.__file.extension() not in self.ALLOWED_EXTENSIONS:
                raise PixieInPipeline(
                    f"Document file has invalid extension: "
                    f"{self.__file.extension()}; "
                    f"Valid extensions: "
                    f"{self.ALLOWED_EXTENSIONS}"
                )
        super(Document, self).__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, Document):
            return other.__file == self.__file and other.to_dict() == self.to_dict()
        return False

    def delete(self):
        """
        Delete Document file
        """
        self.__file.delete()

    def exists(self):
        """
        Check if Document file exists

        :rtype: bool
        """
        return self.__file.exists()

    def file(self):
        """
        Get Document file instance

        :rtype: File
        """
        return self.__file

    # def atom(self):
    #     return self.__atom
    #
    # def key(self):
    #     return self.__atom.key()
    #
    # def zulu(self):
    #     return self.__atom.zulu()
    #
    # def identity(self):
    #     return self.__atom.identity()

    def modified(self):
        """
        Get Document modified date

        :rtype: Zulu
        """
        return self.__created

    def created(self):
        """
        Get Document created date

        :rtype: Zulu
        """
        return self.__modified

    def to_doc(self):
        """
        Get attributes as serializable dictionary

        :rtype: dict
        """
        doc = super(Document, self).to_doc()
        doc["__created"] = self.__created.seed()
        doc["__modified"] = self.__modified.seed()
        doc["atom"] = self.atom.seed()
        return doc

    @classmethod
    def from_doc(cls, doc: dict):
        """
        Create Document file from serialized dictionary

        :param doc: Input dictionary
        :rtype: Document
        """

        created = doc.pop("__created")
        modified = doc.pop("__modified")
        doc["atom"] = Atom.from_seed(doc["atom"])
        doc_file = cls(**doc)
        doc_file.__created = Zulu.from_seed(created)
        doc_file.__modified = Zulu.from_seed(modified)
        return doc_file

    def save(
        self,
        human: bool = False,
        crypt_key: bytes = None,
        password: str = None,
        **kwargs,
    ):
        """
        Save Document
        """
        now = Zulu.now()
        if not self.exists():
            self.__created = now
        self.__modified = now
        if self.__file.extension() == File.JSON_EXTENSION:
            doc_str = self.to_json(human=human)
        elif self.__file.extension() == File.YAML_EXTENSION:
            doc_str = self.to_yaml()
        else:
            raise DocumentError(f"Invalid extension: " f"{self.__file.extension()}")
        if crypt_key:
            self.__crypt_key = crypt_key
        if password:
            self.__password = password
        self.__file.write(doc_str, crypt_key=self.__crypt_key, password=self.__password)
