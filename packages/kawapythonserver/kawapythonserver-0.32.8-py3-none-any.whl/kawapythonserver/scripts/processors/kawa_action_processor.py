import typing
from abc import ABC, abstractmethod

import pandas as pd


class ActionProcessor(ABC):

    @abstractmethod
    def load(self, df: pd.DataFrame):
        pass

    # list of dataframes only for workflow
    @abstractmethod
    def retrieve_data(self) -> pd.DataFrame | list[pd.DataFrame]:
        pass

    def need_defined_outputs(self) -> bool:
        return True

    def dump_metadata(self, to_dump):
        pass

    def data_source_id(self) -> typing.Optional[str]:
        return None
