# studio.py

import sys
import enum
import socket
import lupa
from typing import Any
import importlib

import nanosurf.lib.spm.studio.wrapper as studio_wrapper

try:
    import nanosurf.lib.spm.studio.wrapper.cmd_tree_main as main
    import nanosurf.lib.spm.studio.wrapper.cmd_tree_spm as spm
    import nanosurf.lib.spm.studio.wrapper.cmd_tree_ctrl as ctrl
except ImportError:
    pass
except AttributeError:
    pass

class ScriptContext(enum.IntEnum):
    Main = 0
    SPM  = 1
    Ctrl = 2

g_default_ip_addr = "127.0.0.1"
g_default_ip_port = 33030

class StudioScriptInterface():
    """ This class implements the communication protocol with Studio.

        Usage
        -----

        First use connect() to establish the ip-socket.
        
        Then use execute_command() to communicate with studio. 
        More details see below.


        Implementation
        --------------

        Communication is done over ip-sockets. In most cases by "local host: 127.0.0.1" and predefined standard port 33030
            
        Commands are sent to studio as strings. 
        
        All communications are prompted by a string in this format: "{status, {result}}"
        status = 0 means no error and the result contains the result value of the command. This can be any valid Lua variable including a table itself 
        status = 1 means an error occurred and the result table contains a string with the error message. 
    """
    def __init__(self):
        self.socket:socket.socket = None
        self.server_ip = "" 
        self.server_port = 0
        self._is_server_connected = False
        self._last_error = ""

    def connect(self, host: str = g_default_ip_addr, port: int = g_default_ip_port) -> bool:
        """ Establish a connection to a running instance of studio over ip-socket

        Parameters
        ----------
        host, optional
            hosts ip-address 
        port, optional
            hosts listening port number

        Returns
        -------
            True if connection could be established. Otherwise read error message in last_error property
        """
        self.server_ip = host
        self.server_port = port 
        self.receive_buffer_size = 2**14
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server_ip, self.server_port))
            self._is_server_connected = True
            self._last_error = ""
        except socket.error as er:
            self._is_server_connected = False
            self._last_error = str(er)
       
        return self.is_connected

    def disconnect(self):
        """ Free up ip-connection to studio. """
        self.studio = None
        del self.socket
        self.socket = None

    @property
    def is_connected(self) -> bool:
        """ Return True if connection to studio host is active and communication can be done."""
        return self._is_server_connected 

    @property
    def last_error(self) -> str:
        return self._last_error

    def execute_command(self, cmd_str: str) -> str:
        """ transmit a command string to studio and wait for the response.
        The execution of the python script is blocked until the response is received from studio

        Parameters
        ----------
        cmd_str
            Any valid command string studio accepts.

        Returns
        -------
            result string in studio format. or None in case of an error. 
            Reason of error can be read from property "self.last_error"
        """
        return_val: str = None
        try:
            # send the cmd_str with length of message as header in the first four bytes
            header_len = 4
            cmd_msg = bytes(cmd_str, encoding='utf-8')
            cmd_len = len(cmd_msg).to_bytes(header_len, signed=False, byteorder='little')
            self.socket.sendall(cmd_len + cmd_msg)

            # wait for answer. It have to be a message with header of 4 bytes describing the length of the actual result string
            res_msg = bytearray()
            rec_buffer = self.socket.recv(self.receive_buffer_size)
            if len(rec_buffer) >= header_len:
                res_len = int.from_bytes(rec_buffer[:header_len], byteorder='little', signed=False)

                rec_buffer = rec_buffer[header_len:]
                res_msg += rec_buffer 
                res_len -= len(rec_buffer)

                while res_len > 0:
                    rec_buffer = self.socket.recv(self.receive_buffer_size)
                    res_msg += rec_buffer 
                    res_len -= len(rec_buffer)

                return_val = res_msg.decode(encoding='utf-8')
            else:
                self._last_error = "Did not receive header with length of buffer"

        except socket.error as er:
            self._last_error = str(er)
        return return_val

class StudioScriptContext(StudioScriptInterface):
    """ This class represents a script context provided from studio.
        It provides comfortable access to the command tree items.

        Usage
        -----

        First use connect() to establish the communication with a session context.

        The complete command tree is read from interface and compiled into a python class tree. 
        The start of the class tree is provided in variable 'self.root'
        
        Alternatively, known command strings can be provided to call(), set() or get()

        Implementation
        --------------

        The commands Studio understands, are organized as command trees in a form like "root.workflow.imaging.start()". 
        Variables are set like "root.workflow.imaging.size = value" and read by just sending the name (e.g. "root.workflow.imaging.size")
        
        Depending on session and context, the command tree vary. Only tree "root.session" is always there.
        To get to know the actual command tree read the variable "root" and you get the serialized tree back as response.

        This command tree reading is done automatically. After the context is selected by connect()
        the complete command tree is read from interface and compiled into a python class tree. 
        The start of the class tree is provided in variable 'self.root'
        
        All communications are prompted by a result table with two arguments. "{status, {result table}}"
        status = 0 means no error and the result table contains the result of the command, 
        status = 1 means an error occurred and the result table contains a string with the error message. 
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root: studio_wrapper.CmdTreeNode = None
        self._session_id = ""
        self._context_id = ScriptContext.Main
        self._lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self._lua_deser_func = self._lua.eval("function(ser_str) local func_c, _ = load('return '..ser_str); return func_c(); end") 
        self._root_table_name = "root_table_get_result"
        self._lua_math_type_check_func = self._lua.eval(f"function(var_name) local func_c, _ = load('return tostring(math.type({self._root_table_name}[2][1].' .. var_name .. '))'); return func_c(); end") 
                
    def connect(self, session: str, context: ScriptContext, host: str = g_default_ip_addr, port: int = g_default_ip_port) -> bool:
        """ Establish a connection to specified session and context.
            
            The complete command tree is read from interface and compiled into a python class tree. 
            The start of the class tree is provided in variable 'self.root'

        Parameters
        ----------
        session:
            name of session to open. Typically a string with serial number of controller. e.g "91-21-004" or simulated controller "91-01-000"
        context:
            context id of to open, Context "Main" is always there. Normally also context "SPM". Others are future extensions

        host, optional
            hosts ip-address, by default local host 
        port, optional
            hosts listening port number, by default standard port number

        Returns
        -------
            True if connection could be established. Otherwise error message in 'last_error' property
        """
        res = super().connect(host, port)
        if res:
            res &= self._activate_context(session, context)
        return res

    def call(self, cmd_str: str, *args, convert_table: bool = True, **kwargs) -> Any:
        """ Calls a function with arbitrary number of arguments and a return value
        
        Parameters
        ----------
        cmd_str:
            command from command tree as string. e.g. "root.workflow.imaging.start"
        args:
            argument list as normal python values. They are converted to string representations for transmitting to studio

        convert_table, optional:
            If set to True then the result is converted to python types. Otherwise the result may be a Lua_type. e.g. lua-table. 

        Returns
        -------
            Type depending on command. Most cases either None, float, str or list. 
            In case an error occurred, property "last_error" is not "" and contains an error description
        """
        self._last_error = ""
        arg_str = self._args_to_string(*args, **kwargs)
        ok, cmd_result = self._process_command(f"return {cmd_str}({arg_str})")
        if ok:
            if lupa.lua_type(cmd_result) == "table" and convert_table:
                cmd_result = self._lua_table_to_python_type(cmd_result, **kwargs)
        if not ok:
            print(self._last_error)
        return cmd_result

    def get(self, lua_str: str, convert_table: bool = True, **kwargs) -> Any:
        """ Reads the current value of variable in the command tree.
        
        Parameters
        ----------
        lua_str:
            string of the command tree variable to read. e.g. "root.workflow.imaging.size"

        convert_table, optional:
            If set to True then the result is converted to python types. Otherwise the result may be a Lua_type. e.g. lua-table. 

        Returns
        -------
            Type depending on variable. Most cases either None, float, str or list. 
            In case an error occurred, property "last_error" is not "" and contains an error description
        """
        self._last_error = ""
        ok, cmd_result = self._process_command(f"return {lua_str}")
        if ok:
            if lupa.lua_type(cmd_result) == "table" and convert_table:
                cmd_result = self._lua_table_to_python_type(cmd_result, **kwargs)
        if not ok:
            print(self._last_error)
        return cmd_result

    def set(self, lua_str: str, arg: Any, **kwargs) -> bool:
        """ set variable in the command tree to a new value.
        
        Parameters
        ----------
        lua_str:
            string of the command tree variable to set. e.g. "root.workflow.imaging.size"
        arg:
            new value to set as normal python type. It is converted to string representations for transmitting to studio

        Returns
        -------
            ok: 
                returns True if succeeded to set value, otherwise False and property "last_error" contains an error description
        """     
        ok = False   
        self._last_error = ""
        if lupa.lua_type(arg) != "table":
            arg = self._args_to_string(arg,**kwargs)
            ok, _ = self._process_command(f"{lua_str}={arg}; return 0")
        else:
            ok = False
            self._last_error = "Error: Cannot set lua table directly. It have to be serialized first."
        
        if not ok:
            print(self._last_error)
        return ok

    def load_studio_root_table(self, lua_str: str) -> Any:
        res_val: dict = None
        return_val = self.execute_command(f"return {lua_str}")
        if return_val is not None:
            try:
                self._lua.execute(f"{self._root_table_name} = {return_val}")

                lua_deser_table = self._lua_deser_func(return_val)
                lua_ok = lua_deser_table[1] == 0
                res_val = lua_deser_table[2][1]
                if not lua_ok:
                    self._last_error = f"Scripting: {str(res_val)}"
                    res_val = None
            except lupa._lupa.LuaError as er:
                self._last_error = f"Lupa Error: {er}:\n{return_val}"
            except lupa._lupa.LuaSyntaxError:
                self._last_error = f"Lupa SyntaxError:\n{return_val}"
            except TypeError:
                self._last_error = f"Lupa TypeError:\n{return_val}"
        return res_val

    def lua_type(self, obj) -> str:
        """ convenient function to evaluate the type of a result variable. 
            If the obj provided is a lua type, then the type name is returned. Otherwise None.
            Details see lupa package documentation for lua_type()
        """
        return lupa.lua_type(obj)

    def lua_number_type_str(self, value_name : str) -> str:
        if "root." in value_name:
            value_name = value_name.removeprefix("root.")
        num_type_str = self._lua_math_type_check_func(value_name)
        return num_type_str

    def _process_command(self, cmd_str: str) -> tuple[bool, Any]:
        res_ok = False
        res_val: dict = None
        return_val = self.execute_command(cmd_str)
        if return_val is not None:
            try:
                lua_deser_table = self._lua_deser_func(return_val)
                lua_ok = lua_deser_table[1] == 0
                res_val = lua_deser_table[2][1]
                if not lua_ok:
                    self._last_error = f"Scripting: {str(res_val)}"
                    res_val = None
                res_ok = lua_ok
            except lupa._lupa.LuaError as er:
                self._last_error = f"Lupa Error: {er}:\n{return_val}"
            except lupa._lupa.LuaSyntaxError:
                self._last_error = f"Lupa SyntaxError:\n{return_val}"
            except TypeError:
                self._last_error = f"Lupa TypeError:\n{return_val}"
        return (res_ok, res_val)

    def _python_to_lua_str(self, val:str) -> str:
        cmd_str = val
        cmd_str = cmd_str.replace('\\', '\\\\')
        cmd_str = cmd_str.replace('"', '\\"')
        cmd_str = cmd_str.replace("'", "\\'")
        return cmd_str

    def _python_list_to_lua_table(self, val:list) -> str:
        if len(val) > 0:
            if isinstance(val[0], enum.Enum):
                val = [e.value for e in val]
        return str(val).removeprefix('[').removesuffix(']')

    def _python_dict_to_lua_table(self, val:dict, parse_tree: bool = True) -> str:
        """ Generate lua tables from a python dict . 
            if key 'parse_tree' is True, It handles hierarchical sub dicts
            Return string can be parsed by lua to generate a lua table instance
        """
        res = ""
        for key, value in val.items():
            # if type(value) == dict:
            #     value = self._python_dict_to_lua_table(value)
            res += f"{key}={self._args_to_string(value, parse_tree=parse_tree)},"
        return '{' + res.removesuffix(',') + '}'

    def _lua_table_to_python_type(self, lua_table_val, parse_tree: bool = True) -> dict | list:
        """ Generate python compatible dictionary from a lua table. 
            if key 'parse_tree' is True, It handles hierarchical sub tables 
            it returns either a dict if table has named keywords otherwise a list 
        """
        if self._has_lua_table_keywords(lua_table_val):
            new_dict = dict(lua_table_val)    
            if parse_tree:
                for key, value in new_dict.items():
                    if lupa.lua_type(value) == "table":
                        new_dict[key] = self._lua_table_to_python_type(value, parse_tree)
            return new_dict
        else:
            new_list = list(lua_table_val.values())
            if parse_tree:
                for index in range(len(new_list)):
                    value = new_list[index]
                    if lupa.lua_type(value) == "table":
                        new_list[index] = self._lua_table_to_python_type(value, parse_tree)
        return new_list

    def _args_to_string(self, *args, parse_tree: bool = True) -> str:
        res = ""
        for a in args:
            if type(a) == str:
                res += "'" + self._python_to_lua_str(a) + "',"
            elif type(a) == bool:
                res += str(a).lower()
            elif type(a) == list:
                res += '{' + self._python_list_to_lua_table(a) + '},'
            elif (type(a) == dict) or (lupa.lua_type(a) == "table"):
                res += self._python_dict_to_lua_table(a, parse_tree=parse_tree) + ','
            elif isinstance(a, studio_wrapper.CmdTreeNode):
                res += a._lua_tree_name + ","
            else:
                res += str(a) + ","
        return res.removesuffix(",")

    def _has_lua_table_keywords(self, val) -> bool:
        has_keyword = False
        for key, _ in val.items():
            if isinstance(key, str):
                has_keyword = True
                break
        return has_keyword
    
    def _activate_context(self, session:str, context: ScriptContext) -> bool:
        ok = True
        self._session_id = session
        self._context_id = context
        
        if context == ScriptContext.Main:
            self.call("root.session.select_main", 0)
            ok &= (self.last_error == "") 
        else:
            self.call("root.session.select", self._session_id, context.value)
            ok &= (self.last_error == "") 

        if ok:
            ok &= self._init_cmd_tree()
        return ok

    def _init_cmd_tree(self) -> bool:
        print(f"Init context: {self._context_id.name.lower()}")
        compiler = studio_wrapper.CmdTreeCompiler(self)
        root_table = self.load_studio_root_table("root")
        compiler.build_wrapper_class(self._context_id.name.lower(), root_table)
        self.root = None
        try:
            if self._context_id == ScriptContext.Main:
                cmd_tree_module = sys.modules['nanosurf.lib.spm.studio.wrapper.cmd_tree_main']
            elif self._context_id == ScriptContext.SPM:
                cmd_tree_module = sys.modules['nanosurf.lib.spm.studio.wrapper.cmd_tree_spm']
            elif self._context_id == ScriptContext.Ctrl:
                cmd_tree_module = sys.modules['nanosurf.lib.spm.studio.wrapper.cmd_tree_ctrl']
            else:
                raise ValueError(f"Unknown Context ID found: {self._context_id=}")
            cmd_tree = importlib.reload(cmd_tree_module)    
            self.root = cmd_tree.Root(self)
        except Exception:
            pass
        return self.root is not None 

class StudioScriptSession():
    """ This class represents a single studio script session.
        It provides comfortable access to the command tree items of each context.
        Auto detection of active session is provided and auto activation of all contexts.

        Usage
        -----

        First use connect() to establish the communication with a session.
        If no session is provided, it try to auto-detect the active session

        For all available contexts, it creates a member variable of type StudioScriptContext

        Implementation
        --------------

        All Lua-script context of a sessions are created and stored in a variable self._context
    """  
    def __init__(self):
        # initialize all contexts and its short cuts
        self._context: dict[ScriptContext, StudioScriptContext] = {c: None for c in ScriptContext}
        self.main: main.Root = None
        self.spm: spm.Root = None
        self.ctrl: cmd_tree_ctrl.Root = None

        # socket interface
        self.server_ip = ""
        self.server_port = 0 
        self.session_id = ""

    def connect(self, session: str = "", host: str = g_default_ip_addr, port: int = g_default_ip_port) -> bool:
        """ Establish a connection to a running instance of studio over ip-socket

        Parameters
        ----------
        session, optional:
            name of session to open, by default auto selection of session is used
        host, optional
            hosts ip-address, by default local host 
        port, optional
            hosts listening port number, by default standard port number

        Returns
        -------
            True if connection could be established. Otherwise error message in 'last_error' property
        """
        self.server_ip = host
        self.server_port = port 
        self.session_id = session
        self._last_error = ""

        # clear all context
        self._context: dict[ScriptContext,StudioScriptContext] = {c: None for c in ScriptContext}

        # setup all context
        self._context[ScriptContext.Main] = self.create_context(ScriptContext.Main)
        if self._context[ScriptContext.Main] is not None:

            if self.session_id == "":
                self.session_id = self.auto_select_session()

            if self.session_id != "":
                self._context[ScriptContext.SPM] = self.create_context(ScriptContext.SPM)
                #self._context[ScriptContext.Ctrl] = self.create_context(ScriptContext.Ctrl) # Controller Context not yet available
            else:
                self._last_error = "No session active"

        # assign short cuts to context command trees
        self.main = self._context[ScriptContext.Main].root if self._context[ScriptContext.Main] is not None else None
        self.spm  = self._context[ScriptContext.SPM].root  if self._context[ScriptContext.SPM]  is not None else None
        self.ctrl = self._context[ScriptContext.Ctrl].root if self._context[ScriptContext.Ctrl] is not None else None

        return (self.main is not None) and (self.spm is not None)

    def auto_select_session(self) -> str:
        session_list = self.get_sessions()
        return session_list.pop() if len(session_list) > 0 else ""

    def create_context(self, context: ScriptContext) -> StudioScriptContext:
        new_context = StudioScriptContext()
        ok = new_context.connect(self.session_id, context, self.server_ip, self.server_port)
        if not(ok):
            self._last_error = f"Connect to session '{self.session_id}' context '{context}' failed.\nReason: '{new_context.last_error}'"
            new_context = None
        return new_context

    def get_sessions(self, session: str = None) -> list[str]:
        sessions = []
        if self._context[ScriptContext.Main] is not None:
            sessions = self._context[ScriptContext.Main].root.session.list()
        return sessions

    def disconnect(self):
        """ Close all session nodes"""
        for val in self._context.values():
            if val is not None:
                val.disconnect()

    @property
    def is_connected(self) -> bool:
        """ Return True if connection to studio host is active and communication can be done."""
        return self.main is not None

    @property
    def last_error(self) -> str:
        return self._last_error

class Studio(StudioScriptSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def is_studio(self):
        return True
    
    def is_scripting_enabled(self) -> bool:
        return True

    def get_sw_version(self) -> tuple[int,int,int,int]:
        sw_version = (0,0,0,0)
        try:
            major = self.main.version.major()
            minor = self.main.version.minor()
            revision = 0
            bugfix = 0
            sw_version = (int(major), int(minor), int(revision), int(bugfix))
        except Exception:
            pass # version information is only available since studio 11.x 
        return sw_version