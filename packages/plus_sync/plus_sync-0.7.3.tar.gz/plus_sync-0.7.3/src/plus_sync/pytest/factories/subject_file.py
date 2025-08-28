from pathlib import Path
from typing import Optional

import factory
from attrs import define, field

from plus_sync.hashing import SubjectIDHasher


@define(kw_only=True)
class SubjectFile:
    subject_id: str = field()
    postfix: Optional[str] = field(default=None)
    extension: str = field(default='txt')
    content: str = field()
    path: str = field(default=None)

    @property
    def hashed_subject_id(self) -> str:
        hasher = SubjectIDHasher.from_cmdargs()
        return hasher.hash_subject_id(self.subject_id)

    @property
    def filename(self) -> str:
        postfix = f'_{self.postfix}' if self.postfix else ''
        return f'{self.subject_id}{postfix}.{self.extension}'

    @property
    def hashed_filename(self) -> str:
        postfix = f'_{self.postfix}' if self.postfix else ''
        return f'{self.hashed_subject_id}{postfix}.{self.extension}'

    @property
    def full_path(self) -> str:
        path = self.path or ''
        return f'{path}/{self.filename}'

    @property
    def full_path_parts(self) -> list[str]:
        return [x for x in self.full_path.split('/') if x]

    def save_to_disk(self, root_path: Path) -> None:
        full_path = Path(root_path, self.full_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(self.content)

    @staticmethod
    def create_content_for_sftp(files: list['SubjectFile']) -> dict[str, str]:
        all_content: dict = {}
        for file in files:
            next_content = all_content
            for part in file.full_path_parts:
                content = next_content
                if part not in content:
                    content[part] = {}
                next_content = content[part]

            content[part] = file.content

        return all_content


class SubjectFileFactory(factory.Factory):
    class Meta:
        model = SubjectFile

    content = factory.Faker('sentence')
    extension = 'txt'
    postfix = factory.Faker('word')

    class Params:
        lowercase: bool = True

    @factory.lazy_attribute
    def subject_id(self) -> str:
        faker = factory.Faker._get_faker()
        b_day = faker.date_of_birth()
        b_day_str = b_day.strftime('%Y%m%d')
        initials = faker.first_name()[:2] + faker.last_name()[:2]
        res = f'{b_day_str}{initials}'
        if self.lowercase:  # type: ignore
            return res.lower()
        return res.upper()
