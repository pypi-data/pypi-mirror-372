from typing import Any, Iterator, MutableMapping, MutableSequence, Union, Iterable


class DataPath:

    _PathToken = Union[str, int]  # str for dict keys, int for list indices

    def __init__(self, *parts: _PathToken, filename: str = None):
        self.tokens = list(parts or [])
        for part in self.tokens:
            if part.__class__ is not str and part.__class__ is not int:
                raise ValueError(f"Got a {part.__class__.__name__} as a token.  Probably wrapped path in a container")
        self.filename = filename

    def __truediv__(self, token: _PathToken) -> "DataPath":
        return DataPath(*self.tokens, token, filename=self.filename)

    def __str__(self):
        """
        Format like: "schema.yml sources[2].tables[1]"
        """
        path = ""
        for t in self.tokens:
            if isinstance(t, int):
                path += f"[{t}]"
            else:
                path += ("" if path == "" else ".") + str(t)
        if self.filename:
            return f"[{self.filename}] {path}"
        else:
            return path


def _wrap(value: Any, path: DataPath) -> Any:
    if isinstance(value, dict):
        return DictWrapper(value, _path=path)
    if isinstance(value, list):
        return ListWrapper(value, _path=path)
    return value



class _DataWrapper:

    def __init__(self, data: Any, *, _path: DataPath | None = None, filename: str = None):
        self._data = data

        if _path and filename:
            raise ValueError("Don't provide both _path and filename")
        if filename:
            self._path = DataPath(filename=filename)
        else:
            self._path = _path or DataPath()

class DictWrapper(_DataWrapper):
    """
    Read-only wrapper for dicts that tracks access path and raises
    descriptive KeyError messages on missing keys.

    - data['sources'] -> ListWrapper (iterable)
    - for system in data['sources']: ...
    - system['tables'] -> ListWrapper
    - table['name'] -> str, or KeyError with full path

    You can still use .get(key, default) to avoid raising.
    """

    def __init__(self, data: MutableMapping[str, Any], *, _path: DataPath | None = None, filename: str = None):
        if not isinstance(data, dict):
            raise TypeError(f"DictWrapper expects a dict, got {type(data).__name__}")
        super().__init__(data, _path=_path, filename=filename)

    def __getitem__(self, key: str) -> Any:
        """Get key from wrapped data which is required"""
        path = self._path / key
        try:
            return _wrap(self._data[key], path=path)
        except KeyError as e:
            raise KeyError(f"{self._path} is missing key .{key}") from e

    def get(self, key: str, default: Any = None) -> Any:
        path = self._path / key
        try:
            return _wrap(self._data[key], path)
        except KeyError as e:
            return default

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def keys(self):
        return self._data.keys()

    def values(self):
        # Yield wrapped values so downstream access continues to carry path
        for k in self._data.keys():
            yield _wrap(self._data[k], self._path / k)

    def items(self):
        for k, v in self._data.items():
            yield k, _wrap(v, self._path / k)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        # Iterate keys (normal dict behavior)
        return iter(self._data)

    def __repr__(self) -> str:
        return f"<DictWrapper at {self._path or '<root>'} keys={list(self._data.keys())!r}>"


class ListWrapper(_DataWrapper):
    """
    Read-only wrapper for lists that tracks access path and raises
    descriptive errors. Iteration yields wrapped elements (with index path).
    """

    def __init__(self, data: MutableSequence[Any], *, _path: DataPath | None = None, filename: str = None):
        if not isinstance(data, list):
            raise TypeError(f"ListWrapper expects a list, got {type(data).__name__}")
        super().__init__(data, _path=_path, filename=filename)

    def __getitem__(self, idx: int) -> Any:
        path = self._path / idx
        try:
            val = self._data[idx]
        except IndexError:
            raise IndexError(f"{path} is an invalid index (len={len(self._data)})") from None
        return _wrap(val, path)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        for i, v in enumerate(self._data):
            yield _wrap(v, self._path / i)

    def __repr__(self) -> str:
        return f"<ListWrapper at {self._path or '<root>'} len={len(self._data)}>"

