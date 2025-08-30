#!/usr/bin/env python3

################################################################
import BTrees
import persistent

from . import bdlogging

################################################################
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
BTree = BTrees.OOBTree.BTree
################################################################


class _LowerCaseBTree(object):

    def __init__(self, key_string="key_"):
        self.entries = BTree()
        self.key_string = key_string

    def __delitem__(self, attr):
        key = attr
        if isinstance(key, str):
            key = key.lower()
        del self.entries[key]

    def __getattr__(self, attr):

        if "entries" not in self.__dict__:
            raise AttributeError(attr)

        key = attr.lower()
        _key = key

        # logger.error(self.__dict__)
        key_string = self.__dict__["key_string"]
        if isinstance(key, str) and key.startswith(key_string):
            _key = key[len(key_string) :]
            # logger.error(_key)
            try:
                _key = int(_key)
            except ValueError:
                pass

        # logger.error(_key)
        try:
            if _key in self.entries:
                return self.entries[_key]
            elif key in self.entries:
                return self.entries[key]
            else:
                raise AttributeError(attr)
        except TypeError:
            # logger.error(attr)
            raise AttributeError(attr)

    def __setattr__(self, attr, value):

        if persistent.Persistent._p_setattr(self, attr, value):
            return

        self._p_changed = True
        key = attr.lower()
        if key == "entries" or key == "key_string":
            try:
                object.__setattr__(self, key, value)
            except TypeError:
                persistent.Persistent.__setattr__(self, key, value)
        # logger.error(f"set attr {attr} {value}")

        entries = self.entries
        # logger.error(f"set attr {[ e for e in entries.keys()]}")
        if key in entries:
            # logger.error(f"set attr in entries {attr} {value}")
            self.__setitem__(attr, value)
            self.entries._p_changed = True
        else:
            try:
                object.__setattr__(self, attr, value)
            except TypeError:
                persistent.Persistent.__setattr__(self, attr, value)

    def __getitem__(self, index):
        if isinstance(index, str):
            index = index.lower()
        return self.entries[index]

    def keys(self):
        return self.entries.keys()

    def __iter__(self):
        return self.entries.__iter__()

    def __setitem__(self, index, value):
        if isinstance(index, str):
            index = index.lower()
        self.entries[index] = value

    def items(self):
        # logger.error(f'{[e for e in self.entries.items()]}')
        return self.entries.items()

    def __deepcopy__(self, memo):
        cp = self.__class__()
        for k, v in self.entries.items():
            cp.entries[k] = v
        return cp

    def setEntries(self, params):
        for p, val in params.items():
            if p in self.types:
                self.entries[p] = val

    def __dir__(self):
        def valid_start_character(_str):
            return not _str[0].isdigit()

        return (
            [
                e
                for e in self.entries.keys()
                if isinstance(e, str) and valid_start_character(e)
            ]
            + [
                f"{self.key_string}{e}"
                for e in self.entries.keys()
                if isinstance(e, str) and not valid_start_character(e)
            ]
            + [
                f"{self.key_string}{e}"
                for e in self.entries.keys()
                if isinstance(e, int)
            ]
        )


################################################################


class PersistentLowerCaseBTree(persistent.Persistent, _LowerCaseBTree):
    def __init__(self, *args, **kwargs):
        persistent.Persistent.__init__(self)
        _LowerCaseBTree.__init__(self, *args, **kwargs)
