# studio_wrapper.py

import enum
from typing import Any
import nanosurf.lib.spm.studio.wrapper as wrap

g_cmd_tree_hash = 'e87659c4cd1da3a077907090ffe3591d'
g_compiler_version = '2.5'

class RootCoreHw_modules(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.hw_modules'


class RootCoreI2c(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.i2c'


class RootCoreScript_server(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.script_server'


class RootCoreFluid_fm(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.fluid_fm'


class RootCoreHwm(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.hwm'


class RootCoreSpm_probes_database(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spm_probes_database'


class RootCoreStorage(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.storage'

    def is_file_open(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.storage.is_file_open', *args, **kwargs)

    def open_file(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.storage.open_file', *args, **kwargs)


class RootCoreStageSignal(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.stage.signal'


class RootCoreStage(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.stage'
        self.signal = RootCoreStageSignal(self._context)

    def add_stage(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.stage.add_stage', *args, **kwargs)

    def stages(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.stage.stages', *args, **kwargs)

    def delete_instance(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.stage.delete_instance', *args, **kwargs)

    def instances(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.stage.instances', *args, **kwargs)

    def create_instance(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.stage.create_instance', *args, **kwargs)

    def init_stages(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.stage.init_stages', *args, **kwargs)

    def remove_stage(self, *args, **kwargs) -> Any:
        return self._context.call('root.core.stage.remove_stage', *args, **kwargs)


class RootCoreVshi(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.vshi'


class RootCoreSpm_controller_discovery(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.spm_controller_discovery'


class RootCoreCamera(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.camera'


class RootCoreOptions_store(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core.options_store'


class RootCore(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.core'
        self.options_store = RootCoreOptions_store(self._context)
        self.camera = RootCoreCamera(self._context)
        self.spm_controller_discovery = RootCoreSpm_controller_discovery(self._context)
        self.vshi = RootCoreVshi(self._context)
        self.stage = RootCoreStage(self._context)
        self.storage = RootCoreStorage(self._context)
        self.spm_probes_database = RootCoreSpm_probes_database(self._context)
        self.hwm = RootCoreHwm(self._context)
        self.fluid_fm = RootCoreFluid_fm(self._context)
        self.script_server = RootCoreScript_server(self._context)
        self.i2c = RootCoreI2c(self._context)
        self.hw_modules = RootCoreHw_modules(self._context)


class RootUtil(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.util'

    def table_append(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.table_append', *args, **kwargs)

    def to_string(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.to_string', *args, **kwargs)

    def deep_copy(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.deep_copy', *args, **kwargs)

    def array_concat(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.array_concat', *args, **kwargs)

    def list_table_vars(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.list_table_vars', *args, **kwargs)

    def to_snake_case(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.to_snake_case', *args, **kwargs)

    def prequire(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.prequire', *args, **kwargs)

    def num_table_invert(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.num_table_invert', *args, **kwargs)

    def make_property(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.make_property', *args, **kwargs)

    def list_table_tables(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.list_table_tables', *args, **kwargs)

    def list_table_all(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.list_table_all', *args, **kwargs)

    def list_table_functions(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.list_table_functions', *args, **kwargs)

    def lock_table(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.lock_table', *args, **kwargs)

    def list_table_elements(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.list_table_elements', *args, **kwargs)

    def filter_string_array_begin(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.filter_string_array_begin', *args, **kwargs)

    def deep_compare(self, *args, **kwargs) -> Any:
        return self._context.call('root.util.deep_compare', *args, **kwargs)


class RootSession(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.session'

    @property
    def current_connection(self) -> str:
        return str(self._context.get('root.session.current_connection'))

    @current_connection.setter
    def current_connection(self, new_val:str):
        self._context.set('root.session.current_connection', str(new_val))

    def list(self, *args, **kwargs) -> Any:
        return self._context.call('root.session.list', *args, **kwargs)

    def select_main(self, *args, **kwargs) -> Any:
        return self._context.call('root.session.select_main', *args, **kwargs)

    @property
    def name(self) -> str:
        return str(self._context.get('root.session.name'))

    @name.setter
    def name(self, new_val:str):
        self._context.set('root.session.name', str(new_val))

    def select(self, *args, **kwargs) -> Any:
        return self._context.call('root.session.select', *args, **kwargs)


class RootVersion(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.version'

    def major(self, *args, **kwargs) -> Any:
        return self._context.call('root.version.major', *args, **kwargs)

    def git_commit_hash_short(self, *args, **kwargs) -> Any:
        return self._context.call('root.version.git_commit_hash_short', *args, **kwargs)

    def compile_date_time(self, *args, **kwargs) -> Any:
        return self._context.call('root.version.compile_date_time', *args, **kwargs)

    def name(self, *args, **kwargs) -> Any:
        return self._context.call('root.version.name', *args, **kwargs)

    def minor(self, *args, **kwargs) -> Any:
        return self._context.call('root.version.minor', *args, **kwargs)

    def full(self, *args, **kwargs) -> Any:
        return self._context.call('root.version.full', *args, **kwargs)

    def git_branch(self, *args, **kwargs) -> Any:
        return self._context.call('root.version.git_branch', *args, **kwargs)


class RootWorkflowCamera(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.camera'

    def get_exposure(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.get_exposure', *args, **kwargs)

    def has_gain_auto(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.has_gain_auto', *args, **kwargs)

    def resolution_list(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.resolution_list', *args, **kwargs)

    def move_focus_down_for_duration(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.move_focus_down_for_duration', *args, **kwargs)

    def camera_list(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.camera_list', *args, **kwargs)

    def get_illumination(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.get_illumination', *args, **kwargs)

    def get_gain(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.get_gain', *args, **kwargs)

    def set_exposure_auto(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.set_exposure_auto', *args, **kwargs)

    def get_resolution(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.get_resolution', *args, **kwargs)

    def get_focus(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.get_focus', *args, **kwargs)

    def set_resolution(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.set_resolution', *args, **kwargs)

    def move_focus_by_distance(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.move_focus_by_distance', *args, **kwargs)

    def set_illumination(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.set_illumination', *args, **kwargs)

    def focus_idle(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.focus_idle', *args, **kwargs)

    def has_exposure_auto(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.has_exposure_auto', *args, **kwargs)

    def set_gain_auto(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.set_gain_auto', *args, **kwargs)

    def get_gain_auto(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.get_gain_auto', *args, **kwargs)

    def get_exposure_auto(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.get_exposure_auto', *args, **kwargs)

    def has_focus(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.has_focus', *args, **kwargs)

    def set_exposure(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.set_exposure', *args, **kwargs)

    def save_current_frame_to_file(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.save_current_frame_to_file', *args, **kwargs)

    def has_illumination(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.has_illumination', *args, **kwargs)

    def is_connected(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.is_connected', *args, **kwargs)

    def move_focus_up_for_duration(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.move_focus_up_for_duration', *args, **kwargs)

    def set_gain(self, *args, **kwargs) -> Any:
        return self._context.call('root.workflow.camera.set_gain', *args, **kwargs)


class RootWorkflowManager(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.manager'

    @property
    def session_name(self) -> str:
        return str(self._context.get('root.workflow.manager.session_name'))

    @session_name.setter
    def session_name(self, new_val:str):
        self._context.set('root.workflow.manager.session_name', str(new_val))


class RootWorkflowHardware_detection(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.hardware_detection'


class RootWorkflowParameters(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.parameters'


class RootWorkflowApplication_updater(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.application_updater'


class RootWorkflowCantilever_browser(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow.cantilever_browser'


class RootWorkflow(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root.workflow'
        self.cantilever_browser = RootWorkflowCantilever_browser(self._context)
        self.application_updater = RootWorkflowApplication_updater(self._context)
        self.parameters = RootWorkflowParameters(self._context)
        self.hardware_detection = RootWorkflowHardware_detection(self._context)
        self.manager = RootWorkflowManager(self._context)
        self.camera = RootWorkflowCamera(self._context)


class Root(wrap.CmdTreeNode):
    def __init__(self, context: 'StudioScriptContext'):
        super().__init__()
        self._context = context
        self._lua_tree_name = 'root'
        self.workflow = RootWorkflow(self._context)
        self.version = RootVersion(self._context)
        self.session = RootSession(self._context)
        self.util = RootUtil(self._context)
        self.core = RootCore(self._context)

    def log_info(self, *args, **kwargs) -> Any:
        return self._context.call('root.log_info', *args, **kwargs)

    def log_warn(self, *args, **kwargs) -> Any:
        return self._context.call('root.log_warn', *args, **kwargs)

    @property
    def init_complete(self) -> bool:
        return bool(self._context.get('root.init_complete'))

    @init_complete.setter
    def init_complete(self, new_val:bool):
        self._context.set('root.init_complete', bool(new_val))

    def log_fatal(self, *args, **kwargs) -> Any:
        return self._context.call('root.log_fatal', *args, **kwargs)

    def log_error(self, *args, **kwargs) -> Any:
        return self._context.call('root.log_error', *args, **kwargs)

    def log_debug(self, *args, **kwargs) -> Any:
        return self._context.call('root.log_debug', *args, **kwargs)


