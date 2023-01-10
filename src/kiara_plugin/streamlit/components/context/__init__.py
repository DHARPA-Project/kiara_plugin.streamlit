# -*- coding: utf-8 -*-
from typing import Any, Callable, List, Union

from pydantic import Field
from streamlit.delta_generator import DeltaGenerator

from kiara_plugin.streamlit.components import ComponentOptions, KiaraComponent


class ContextSwitchOptions(ComponentOptions):
    allow_create: bool = Field(
        description="Allow the user to create a new context.", default=False
    )
    switch_to_selected: bool = Field(
        description="Switch to the selected context.", default=True
    )


class ContextSwitch(KiaraComponent[ContextSwitchOptions]):

    _options = ContextSwitchOptions
    _component_name = "context_switch_control"

    def _render(self, st: DeltaGenerator, options: ContextSwitchOptions) -> bool:

        if not options.allow_create:
            context_names = self.api.list_context_names()
            if "default" in context_names:
                context_names.pop(context_names.index("default"))
                context_names.insert(0, "default")
            current = self.api.current_context_name

            selected_context = self.write_selectbox(
                st=st,
                items=context_names,
                key=["kiara_context", "context_name"],
                options=options,
                default=current,
                label="Select context",
                help="Select the active context.",
            )
            if selected_context != current:
                self.api.set_active_context(selected_context)
                return True
            else:
                return False

        else:

            selectbox_placeholder = st.empty()
            checkbox_key = options.create_key("kiara_context", "new_context_checkbox")

            text_field_key = options.create_key(
                "kiara_context", "context_name", "text_field"
            )

            if self.get_session_var(options, "kiara_context", "created", default=False):
                self.set_session_var(options, "kiara_context", "created", value=False)
                self._st.session_state[text_field_key] = ""
                self._st.session_state[checkbox_key] = False

            create_context_checkbox = st.checkbox(
                "Create new context", key=checkbox_key
            )
            submitted = False
            if create_context_checkbox:
                with st.form(key=options.create_key("context_select_form")):

                    new_context_name = st.text_input(
                        label="Context name", key=text_field_key, value=""
                    )
                    submitted = st.form_submit_button("Create")

            current = self.api.current_context_name
            if submitted:
                print(f"CREATING CONTEXT: {new_context_name}")
                self.api.create_new_context(new_context_name, set_active=False)
                # self.set_session_var(options, "kiara_context", "context_name", value=new_context_name)
                self.set_session_var(options, "kiara_context", "created", value=True)
                force = new_context_name
            else:
                self.set_session_var(options, "kiara_context", "created", value=False)
                force = None

            context_names = self.api.list_context_names()

            if "default" in context_names:
                context_names.pop(context_names.index("default"))
                context_names.insert(0, "default")

            selected_context = self.write_selectbox(
                st=selectbox_placeholder,
                items=context_names,
                options=options,
                key=["kiara_context", "select_context"],
                force=force,
                default=current,
                label="Select context",
                help="Select the active context.",
            )

            if selected_context != current and options.switch_to_selected:
                self.api.set_active_context(selected_context)

            return selected_context

    def write_selectbox(
        self,
        st: DeltaGenerator,
        options: ContextSwitchOptions,
        key: List[str],
        items: List[str],
        force: Any = None,
        default: Any = None,
        label: Union[str, None] = None,
        help: Union[str, None] = None,
        format_func: Callable[[Any], Any] = str,
    ) -> Any:

        value_state_key = options.get_session_key(*key)
        widget_key = options.create_key(*key, "selectbox")

        idx = 0
        if force is not None:
            self._st.session_state[widget_key] = force
            idx = 0
        elif widget_key not in self._st.session_state:
            if default:
                idx = items.index(default)
            else:
                idx = 0

        if not label:
            label = "Select value"

        def _set_current_value():
            self._st.session_state[value_state_key] = self._st.session_state[widget_key]

        result = st.selectbox(
            label=label,
            options=items,
            key=widget_key,
            index=idx,
            on_change=_set_current_value,
            help=help,
            format_func=format_func,
        )

        return result
