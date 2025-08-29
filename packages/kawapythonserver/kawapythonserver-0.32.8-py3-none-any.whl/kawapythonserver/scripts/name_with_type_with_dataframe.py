from dataclasses import dataclass


@dataclass
class NameWithTypeWithDataframe:
    name: str
    type: str
    dataframe: str | None

    @classmethod
    def from_dict(cls, d: dict) -> 'NameWithTypeWithDataframe':
        return cls(d['name'], d['type'], d.get('dataframe'))    # key 'dataframe' may not exist in the dictionary
