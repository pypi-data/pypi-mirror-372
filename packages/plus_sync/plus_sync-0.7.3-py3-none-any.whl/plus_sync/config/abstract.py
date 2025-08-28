from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self, Union

import cattrs
from attrs import define, field, validate
from tomlkit import TOMLDocument, document, parse
from tomlkit.toml_file import TOMLFile

cattrs_converter = cattrs.Converter(forbid_extra_keys=True)


@define()
class AbstractTomlConfig(ABC):
    __parsed_toml: TOMLDocument | None = field(default=None, init=False)

    @classmethod
    def from_toml(cls, f_name: str) -> Self:
        with Path(f_name).open() as f:
            parsed_toml = parse(f.read())
            object = cattrs_converter.structure(parsed_toml, cls)
            object.__parsed_toml = parsed_toml

            return object

    @classmethod
    @abstractmethod
    def _get_config_file(cls) -> str:
        raise NotImplementedError

    @classmethod
    def from_cmdargs(cls) -> Self:
        return cls.from_toml(cls._get_config_file())

    def toml_document(self) -> TOMLDocument:
        as_dict = cattrs_converter.unstructure(self)
        # recursively remove None values
        self.__remove_nones(as_dict)

        parsed_toml = self.__parsed_toml
        if parsed_toml is None:
            parsed_toml = document()

        parsed_toml.update(as_dict)

        return parsed_toml

    def dump(self) -> str:
        parsed_toml = self.toml_document()

        return parsed_toml.as_string()

    def save(self, f_name: Union[str, Path], overwrite: bool = False) -> None:
        validate(self)
        f_name = Path(f_name)
        if f_name.exists() and not overwrite:
            raise FileExistsError(f'File {f_name} already exists. Use overwrite=True to overwrite it.')

        TOMLFile(f_name).write(self.toml_document())

    def __remove_nones(self, d: Union[dict, list]) -> None:
        if isinstance(d, list):
            for value in d:
                if isinstance(value, (dict, list)):
                    self.__remove_nones(value)
            return
        bad_keys = []
        for key, value in d.items():
            if value is None:
                bad_keys.append(key)
            elif isinstance(value, (dict, list)):
                self.__remove_nones(value)

        for key in bad_keys:
            del d[key]
