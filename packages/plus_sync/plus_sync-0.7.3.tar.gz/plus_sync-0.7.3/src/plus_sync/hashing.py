import hashlib
import re

from attrs import define

import plus_sync.config


@define(kw_only=True)
class SubjectIDHasher:
    subject_id_regex: str = r'[12][0-9]{7}[a-zA-Z]{4}'
    project_name: str

    @classmethod
    def from_config(cls, config: 'plus_sync.config.Config') -> 'SubjectIDHasher':
        return cls(subject_id_regex=config.subject_id_regex, project_name=config.project_name)

    @classmethod
    def from_cmdargs(cls) -> 'SubjectIDHasher':
        config = plus_sync.config.Config.from_cmdargs()

        return cls.from_config(config)

    def hash_subject_id(self, subject_id: str) -> str:
        h = hashlib.sha256()
        h.update(subject_id.encode())
        h.update(self.project_name.encode())

        return h.hexdigest()[:12]

    def replace_subject_ids(self, text: str) -> str:
        return re.sub(self.subject_id_regex, lambda x: self.hash_subject_id(x.group()), text)
