# -*- coding: utf-8 -*-
from typing import Any, Dict

from kiara.models.data_types import DictModel
from kiara.models.filesystem import FileBundle, FileModel
from kiara.utils.json import orjson_dumps
from streamlit.delta_generator import DeltaGenerator

from kiara_plugin.streamlit.components.preview import PreviewComponent, PreviewOptions


class DictPreview(PreviewComponent):

    _component_name = "dict_preview"

    @classmethod
    def get_data_type(cls) -> str:
        return "dict"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions) -> None:

        _value = self.api.get_value(options.value)
        dict_data: DictModel = _value.data

        data, schema = st.tabs(["Data", "Schema"])

        try:
            json_str = orjson_dumps(dict_data.dict_data)
        except Exception as e:
            json_str = f"Error parsing data: {e}"
        data.json(json_str)

        try:
            json_str = orjson_dumps(dict_data.data_schema)
        except Exception as e:
            json_str = f"Error parsing schema: {e}"
        schema.json(json_str)

        return


class FileBundlePreview(PreviewComponent):

    _component_name = "file_bundle_preview"

    @classmethod
    def get_data_type(cls) -> str:
        return "file_bundle"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions) -> None:

        _value = self.api.get_value(options.value)
        bundle: FileBundle = _value.data

        table: Dict[str, Any] = {}
        for file_path, file_info in bundle.included_files.items():
            table.setdefault("path", []).append(file_path)
            table.setdefault("size", []).append(file_info.size)
            table.setdefault("mime-type", []).append(file_info.mime_type)

        st.dataframe(table, use_container_width=True)

        return


class FilePreview(PreviewComponent):

    _component_name = "file_preview"

    @classmethod
    def get_data_type(cls) -> str:
        return "file"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions) -> None:

        _value = self.api.get_value(options.value)
        file_model: FileModel = _value.data

        table: Dict[str, Any] = {"key": [], "value": []}
        table["key"].append("path")
        table["value"].append(file_model.path)
        table["key"].append("size")
        table["value"].append(file_model.size)
        table["key"].append("mime-type")
        table["value"].append(file_model.mime_type)
        table["key"].append("content")
        table["value"].append(file_model.read_text())
        st.table(table)

        # st.table(table, use_container_width=True)

        return


class BooleanPreview(PreviewComponent):

    _component_name = "boolean_preview"

    @classmethod
    def get_data_type(self) -> str:
        return "boolean"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions) -> None:

        _value = self.api.get_value(options.value)
        if _value.data is True:
            st.write("true")
        else:
            st.write("false")


class NonePreview(PreviewComponent):

    _component_name = "none_preview"

    @classmethod
    def get_data_type(self) -> str:
        return "none"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions) -> None:

        st.write("-- value not set --")
