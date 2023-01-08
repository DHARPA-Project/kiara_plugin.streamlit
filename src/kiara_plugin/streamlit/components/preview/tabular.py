# -*- coding: utf-8 -*-
import networkx as nx
import streamlit.components.v1 as components
from kiara_plugin.network_analysis.models import NetworkData
from kiara_plugin.tabular.models.array import KiaraArray
from kiara_plugin.tabular.models.db import KiaraDatabase
from kiara_plugin.tabular.models.table import KiaraTable
from pyvis.network import Network
from streamlit.delta_generator import DeltaGenerator

from kiara_plugin.streamlit.components.preview import PreviewComponent, PreviewOptions


class ArrayPreview(PreviewComponent):

    _component_name = "array_preview"

    @classmethod
    def get_data_type(cls) -> str:
        return "array"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions):

        _value = self.api.get_value(options.value)
        table: KiaraArray = _value.data

        st.dataframe(table.to_pandas(), use_container_width=True)


class TablePreview(PreviewComponent):

    _component_name = "table_preview"

    @classmethod
    def get_data_type(cls) -> str:
        return "table"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions):

        _value = self.api.get_value(options.value)
        table: KiaraTable = _value.data

        st.dataframe(table.to_pandas(), use_container_width=True)


class DatabasePreview(PreviewComponent):

    _component_name = "database_preview"

    @classmethod
    def get_data_type(cls) -> str:
        return "database"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions):

        _value = self.api.get_value(options.value)
        db: KiaraDatabase = _value.data
        tabs = st.tabs(list(db.table_names))

        for idx, table_name in enumerate(db.table_names):
            # TODO: this is probably not ideal, as it always loads all tables because
            # of how tabs are implemented in streamlit
            # maybe there is an easy way to do this better, otherwise, maybe not use tabs
            table = db.get_table_as_pandas_df(table_name)
            tabs[idx].dataframe(table, use_container_width=True)


class NetworkDataPreview(PreviewComponent):

    _component_name = "network_data_preview"

    @classmethod
    def get_data_type(cls) -> str:
        return "network_data"

    def render_preview(self, st: DeltaGenerator, options: PreviewOptions):

        _value = self.api.get_value(options.value)
        db: NetworkData = _value.data
        tab_names = ["graph"]
        tab_names.extend(db.table_names)
        tabs = st.tabs(tab_names)

        # graph
        graph_types = ["non-directed", "directed"]
        graph_type = tabs[0].radio("Graph type", graph_types)
        if graph_type == "non-directed":
            graph = db.as_networkx_graph(nx.Graph)
        else:
            graph = db.as_networkx_graph(nx.DiGraph)

        vis_graph = Network(
            height="400px", width="100%", bgcolor="#222222", font_color="white"
        )
        vis_graph.from_nx(graph)
        vis_graph.repulsion(
            node_distance=420,
            central_gravity=0.33,
            spring_length=110,
            spring_strength=0.10,
            damping=0.95,
        )

        html = vis_graph.generate_html()
        with tabs[0]:
            components.html(html, height=435)

        for idx, table_name in enumerate(db.table_names, start=1):
            # TODO: this is probably not ideal, as it always loads all tables because
            # of how tabs are implemented in streamlit
            # maybe there is an easy way to do this better, otherwise, maybe not use tabs
            table = db.get_table_as_pandas_df(table_name)
            tabs[idx].dataframe(table, use_container_width=True)
