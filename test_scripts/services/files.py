import arrow
import json
import os
import pandas as pd

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, List, Optional, Union


OUTPUT_FOLDER = "output_files"
ALLOWED_FILE_EXTENSIONS = ["csv", "xlsx", "json", "txt"]

class SaveFileAbstract(ABC):
    def __init__(self, file_type: str, output_name: Optional[str] = None, **kwargs):
        self._file_type = file_type
        self._output_name = self.__get_output_file_name(output_name=output_name)
        self._select_columns = kwargs.get("columns")

    @classmethod
    def output_folder_exists(cls) -> bool:
        return os.path.exists(OUTPUT_FOLDER)

    @property
    def output_file_path(self) -> str:
        return self._get_output_file_path(extension=self._file_type)

    def _create_output_folder(self) -> None:
        if not self.output_folder_exists():
            os.mkdir(OUTPUT_FOLDER)

    def __get_output_file_name(self, output_name: Optional[str] = None) -> str:
        execution_started_at = arrow.now().format("YYYY-MM-DD_HH-mm-ss")
        output_file_name = os.path.splitext(output_name)[0] if output_name else f"output_{execution_started_at}"

        folder_split = os.path.split(output_file_name)
        has_folders = len(folder_split) > 1 and folder_split[0] != ""
        if not has_folders and not output_name:
            self._create_output_folder()
            output_file_name = os.path.join(OUTPUT_FOLDER, output_file_name)

        if has_folders:
            folder_split_copy = deepcopy(list(folder_split))
            file_name = folder_split_copy.pop()
            if file_name:
                file_name, _ = os.path.splitext(file_name)

            dirs_ = None
            for idx, folder in enumerate(folder_split_copy):
                if dirs_ is None:
                    dirs_ = folder

                if not os.path.exists(dirs_):
                    os.mkdir(dirs_)

                if idx > 0:
                    dirs_ = os.path.join(dirs_, folder)

            output_file_name = os.path.join(dirs_, file_name)

        return output_file_name

    def _get_output_file_path(self, extension: str) -> str:
        return f"{self._output_name}.{extension}"

    @abstractmethod
    def save_data(self, data: Union[str, List[str], Dict[str, List[str]], pd.DataFrame]) -> None:
        raise NotImplementedError


class SaveCSVFile(SaveFileAbstract):
    def save_data(self, data: Union[str, List[str], Dict[str, List[str]], pd.DataFrame]) -> None:
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)

        output_file_path = self._get_output_file_path(extension="csv")

        if self._select_columns:
            data = data[self._select_columns]
        data.to_csv(output_file_path, index=False)


class SaveXLSFile(SaveFileAbstract):
    def save_data(self, data: Union[str, List[str], Dict[str, List[str]], pd.DataFrame]) -> None:
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)

        output_file_path = self._get_output_file_path(extension=self._file_type)

        if self._select_columns:
            data = data[self._select_columns]
        data.to_excel(output_file_path, index=False)


class SaveJSONFile(SaveFileAbstract):
    def save_data(self, data: Union[str, List[str], Dict[str, List[str]], pd.DataFrame]) -> None:
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")

        output_file_path = self._get_output_file_path(extension="json")
        with open(output_file_path, "w") as output_file:
            json.dump(data, output_file, indent=2)


class SaveTXTFile(SaveFileAbstract):
    def save_data(self, data: Union[str, List[str], Dict[str, List[str]], pd.DataFrame]) -> None:
        output_file_path = self._get_output_file_path(extension=self._file_type)
        if isinstance(data, pd.DataFrame):
            if self._select_columns:
                data = data[self._select_columns]

            data.to_csv(output_file_path, index=False)
            return

        with open(output_file_path, "w") as output_file:
            output_file.write(data)


WRITE_FILE_EXTENSIONS_MAP = {
    "csv": SaveCSVFile,
    "json": SaveJSONFile,
    "xls": SaveXLSFile,
    "xlsx": SaveXLSFile,
}


def write_output_file(
    data: Union[str, List[str], Dict[str, List[str]], pd.DataFrame],
    file_type: str,
    output_file_path: Optional[str] = None,
    select_columns: Optional[List[str]] = None,
) -> str:
    class_ = WRITE_FILE_EXTENSIONS_MAP.get(file_type) or SaveTXTFile
    kwargs = {}
    if select_columns:
        kwargs["columns"] = select_columns
    save_file = class_(file_type=file_type, output_name=output_file_path, **kwargs)

    print(f"Writing output file: {save_file.output_file_path}...")
    save_file.save_data(data=data)
    return save_file.output_file_path


class LoadFile(ABC):
    def __init__(self, file_path: str):
        self._file_path = file_path

    @abstractmethod
    def load_data(self) -> Union[str, List[str], Dict[str, List[str]], pd.DataFrame]:
        raise NotImplementedError


class LoadExcelFile(LoadFile):
    def __init__(self, file_path: str, sheet_name: Optional[str] = None, skiprows: Optional[int] = None, header: Optional[int] = None):
        super().__init__(file_path=file_path)
        self._sheet_name = sheet_name
        self._skiprows = skiprows
        self._header = header

    def load_data(self) -> pd.DataFrame:
        return pd.read_excel(
            io=self._file_path,
            sheet_name=self._sheet_name,
            skiprows=self._skiprows,
            header=self._header,
        )


class LoadJSONFile(LoadFile):
    def load_data(self) -> Dict[str, List[str]]:
        with open(self._file_path, "r") as json_file:
            return json.load(json_file)


class LoadCSVFile(LoadFile):
    def __init__(self, file_path: str, skiprows: Optional[int] = None):
        super().__init__(file_path=file_path)
        self._skiprows = skiprows

    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(self._file_path, skiprows=self._skiprows)



LOAD_FILE_EXTENSIONS_MAP = {
    "csv": LoadCSVFile,
    "json": LoadJSONFile,
    "xls": LoadExcelFile,
    "xlsx": LoadExcelFile,
}


def load_file(file_path: str, **kwargs) -> Union[str, List[str], Dict[str, List[str]], pd.DataFrame]:
    _, file_extension = os.path.splitext(file_path)
    file_type = file_extension.replace(".", "")

    class_ = LOAD_FILE_EXTENSIONS_MAP.get(file_type) or LoadCSVFile
    load_file = class_(file_path=file_path, **kwargs)
    return load_file.load_data()
