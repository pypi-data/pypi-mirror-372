from typing import *

from datahold import OkayList

__all__ = ["Holder"]


class Holder(OkayList):
    @property
    def data(self: Self) -> list[str]:
        "This property represents the lines of text."
        return list(self._data)

    @data.setter
    def data(self: Self, value: Iterable, /) -> None:
        normed: list = list()
        x: Any
        for x in value:
            normed += str(x).split("\n")
        self._data = normed

    @data.deleter
    def data(self: Self) -> None:
        self._data = list()

    def dump(self: Self, stream: BinaryIO) -> None:
        "This method dumps the data into a byte stream."
        stream.write(self.dumps().encode())

    def dumpintofile(self: Self, file: Any) -> None:
        "This method dumps the data into a file."
        stream: Any
        item: Any
        with open(file, "w") as stream:
            for item in self:
                print(item, file=stream)

    def dumps(self: Self) -> str:
        "This method dumps the data as a string."
        return "\n".join(self._data) + "\n"

    @classmethod
    def load(cls: type, stream: BinaryIO) -> Self:
        "This classmethod loads a new instance from a given byte stream."
        return cls.loads(stream.read().decode())

    @classmethod
    def loadfromfile(cls: type, file: Any) -> Self:
        "This classmethod loads a new instance from a given file."
        stream: Any
        with open(file, "r") as stream:
            return cls.loads(stream.read())

    @classmethod
    def loads(cls: type, string: Any) -> Self:
        "This classmethod loads a new instance from a given string."
        text: str = str(string)
        if text.endswith("\n"):
            text = text[:-1]
        ans: Self = cls(text.split("\n"))
        return ans
