import uuid
from pathlib import Path
import pickle as pickl
from loguru import logger as log

class PickleClass:
    def __init__(self):
        self._pickle_id = f"pkl-id={str(uuid.uuid4())[:8]}"
        self._pickle_filename = f"{self.__class__.__name__}_{self._pickle_id}.pickle"

    @classmethod
    def from_pickle(cls, path: Path):
        try:
            data = path.read_bytes()
            inst = pickl.loads(data)
            log.debug(f"Successfully loaded from {path}")
            return inst
        except Exception as e:
            log.error(f"Failed to load from {path}: {e}")
            raise

    def to_pickle(self, filename: str = None, cwd: Path = None):
        if filename: name = f"{filename}.pickle"
        else: name = self._pickle_filename
        if not cwd: cwd = Path.cwd()
        file = cwd / name

        try:
            data = pickl.dumps(self)  # Dump the entire instance
            file.write_bytes(data)
            log.debug(f"Pickled to {file}")
            return file
        except Exception as e:
            log.error(f"Failed to pickle to {file}: {e}")
            raise