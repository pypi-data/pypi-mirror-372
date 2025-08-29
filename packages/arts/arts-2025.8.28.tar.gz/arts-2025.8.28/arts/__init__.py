import json
from os.path import abspath
from pathlib import Path


class Dict_file:
    def __init__(self, fpath: str):
        self.fpath = Path(abspath(fpath))
        try:
            self.core = json.loads(self.fpath.read_text(encoding='utf8'))
        except:
            self.core = {}

    def _save(self):
        if not self.fpath.parent.exists():
            self.fpath.parent.mkdir(parents=True, exist_ok=True)
        self.fpath.write_text(json.dumps(self.core, ensure_ascii=False), encoding='utf8')

    def __getitem__(self, key):
        return self.core[key]

    def __setitem__(self, key, value):
        self.core[key] = value
        self._save()

    def update(self, *args, **kwargs):
        self.core.update(*args, **kwargs)
        self._save()

    def keys(self): return self.core.keys()

    def values(self): return self.core.values()

    def items(self): return self.core.items()

    def pop(self, *args, **kwargs):
        result = self.core.pop(*args, **kwargs)
        self._save()
        return result

    def get(self, key, default=None):
        return self.core.get(key, default)
    
    def setdefault(self, key, default=None):
        if key in self.core:
            return self.core[key]
        else:
            result = self.core.setdefault(key, default)
            self._save()
            return result

    def __ior__(self, other):
        self.core |= other
        self._save()
        return self

    def __len__(self):
        return len(self.core)

    def __iter__(self):
        return self.core.__iter__()
