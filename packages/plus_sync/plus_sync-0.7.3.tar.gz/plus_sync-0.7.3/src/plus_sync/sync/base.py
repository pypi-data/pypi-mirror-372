import binascii
import datetime
import hashlib
import importlib
import re
from abc import ABC, abstractmethod
from functools import cache
from pathlib import Path
from typing import Any, Optional

import quickxorhash  # type: ignore
from attrs import define, field

import plus_sync.config
from plus_sync.config.config import BaseRemoteConfig
from plus_sync.hashing import SubjectIDHasher


def _size_converter(size: Any) -> int | None:
    return int(size) if size is not None else None


def _last_modified_converter(last_modified: Any) -> datetime.datetime | None:
    return datetime.datetime.fromisoformat(last_modified) if isinstance(last_modified, str) else None


@define()
class FileInformation:
    path: str = field()
    size: Optional[int] = field(default=None, converter=_size_converter)
    last_modified: Optional[datetime.datetime] = field(converter=_last_modified_converter, default=None)
    hashes: Optional[dict[str, str]] = field(default=None, repr=False)
    exists: bool = field(default=True)

    def hash_subject_ids(self) -> None:
        hasher = SubjectIDHasher.from_cmdargs()
        self.path = hasher.replace_subject_ids(self.path)

    def matches(self, other: 'FileInformation') -> bool:
        match: bool = self.exists and other.exists and self.size == other.size
        if self.hashes is not None and other.hashes is not None:
            all_keys = set(self.hashes.keys()).intersection(other.hashes.keys())
            match = match and all([self.hashes[key] == other.hashes[key] for key in all_keys])
        elif self.hashes is None and other.hashes is None:
            pass
        else:
            match = False

        return match

    def __hash__(self) -> int:
        return hash(self.path) + hash(self.size) + hash(self.last_modified)


class BaseSync(ABC):
    cfg = None

    @abstractmethod
    def __init__(self, cfg: BaseRemoteConfig):
        pass

    @classmethod
    def get_from_config(cls, cfg: BaseRemoteConfig) -> 'BaseSync':
        # get all subclasses of BaseSync
        subclasses = cls.__subclasses__()
        # get the first subclass that matches the config
        for subclass in subclasses:
            # get type annotations of the first parameter of the subclass __init__
            annotation = list(subclass.__init__.__annotations__.values())[0]

            if isinstance(annotation, str):
                module_name, class_name = annotation.rsplit('.', 1)
                module = importlib.import_module(module_name)
                annotation = getattr(module, class_name)

            if cfg.__class__ == annotation:
                obj = subclass(cfg)
                obj.cfg = cfg

                return obj

        raise RuntimeError('No matching subclass found')

    @abstractmethod
    def _get_files(self, with_metadata: bool = True) -> list[FileInformation]:
        pass

    @cache
    def get_files(self, with_metadata: bool = True) -> list[FileInformation]:
        return self._get_files(with_metadata=with_metadata)

    def get_all_subjects(self, hash: bool = True) -> list[str]:
        from plus_sync.config import Config  # noqa PLC0415

        cfg = Config.from_cmdargs()
        all_files = self.get_files(with_metadata=False)
        s_regex = re.compile(cfg.subject_id_regex)

        subjects = []
        for cur_file in all_files:
            match = re.findall(s_regex, cur_file.path)
            if len(match) > 0:
                subjects.append(match[0])

        all_subjects = sorted(set(subjects))
        if hash:
            hasher = SubjectIDHasher.from_config(cfg)

            all_subjects = [hasher.hash_subject_id(x) for x in all_subjects]

        return all_subjects

    def get_files_for_subjects(self, subject_ids: Optional[list[str]] = None) -> list[FileInformation]:
        all_files = self.get_files()
        if subject_ids is not None:
            all_files = [x for x in all_files if any([s_id in x.path for s_id in subject_ids])]

        return all_files

    @abstractmethod
    def get_content(self, file: FileInformation) -> bytes:
        pass

    def get_local_file(
        self, file: FileInformation, hash_subject_ids: bool = True, sync_folder: Path | None = None
    ) -> FileInformation:
        if self.cfg is None:
            raise ValueError('Config not set.')
        config = plus_sync.config.Config.from_cmdargs()
        if sync_folder is None:
            sync_folder = Path(config.sync_folder)
        local_path = Path(sync_folder, self.cfg.name, file.path)
        local_file = FileInformation(path=str(local_path), exists=False)
        if hash_subject_ids:
            local_file.hash_subject_ids()
        if Path(local_file.path).exists():
            local_file.exists = True
            tmp_path = Path(local_file.path)
            local_file.size = tmp_path.stat().st_size
            local_file.last_modified = datetime.datetime.fromtimestamp(tmp_path.stat().st_mtime)
            if file.hashes is not None:
                local_file.hashes = {}
                for hash_name in file.hashes:
                    if hash_name == 'sha256':
                        h = hashlib.sha256()
                        with tmp_path.open('rb') as f:
                            h.update(f.read())
                        local_file.hashes[hash_name] = h.hexdigest()
                    if hash_name == 'quickxor':
                        h = quickxorhash.quickxorhash()
                        with tmp_path.open('rb') as f:
                            h.update(f.read())
                        local_file.hashes[hash_name] = binascii.hexlify(h.digest()).decode()
        return local_file
