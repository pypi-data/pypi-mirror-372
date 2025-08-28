% if version >= 4:
${make_header('lua')}
<%namespace name="imports" file="utils/imports.mako"/>
<%namespace name="default_intf" file="utils/default_intf.lua.mako"/>
<%namespace name="mdb_obj" file= "utils/mdb_obj.lua.mako"/>
<% has_signal = root['signals']%>
<% has_mdb = any('path' in cls_data for cls, cls_data in root['class_require'].items())%>
<% has_default = any((rpc['default'] != '' and not rpc['override']) for rpc in root['methods'])%>
<% ClassName = root['package'] + '_service' %>

% if root['has_ipmi_cmd']:
local ipmi = require 'ipmi'
% endif
% if has_default or has_mdb:
local mdb = require 'mc.mdb'
% endif
% if utils_py.check_local_reset_db(root) or utils_py.check_local_temporary_db(root):
local skynet = require 'skynet'
% endif
local class = require 'mc.class'
% if has_signal:
local context = require 'mc.context'
% endif
% if utils_py.check_need_mem_db(root):
local open_db = require '${project_name}.db'
% endif
% if root['path_level'] == 2:
local app_base = require 'mc.service_app_base'
% endif
% if utils_py.check_local_poweroff_db(root) or utils_py.check_local_reset_db(root) or utils_py.check_local_temporary_db(root):
local open_local_db = require '${project_name}.local_db'
% endif
% if (root['path_level'] == 2 and utils_py.check_db_open(root['package']) and utils_py.check_remote_per(root)) or root['class_require']:
local object_manage = require 'mc.mdb.object_manage'
% endif
% if root['path_level'] == 2 and utils_py.check_db_open(root['package']) and utils_py.check_remote_per(root):
local persist_client = require 'persistence.persist_client_lib'
% endif
% if utils_py.check_need_mem_db(root):
local orm_classes = require '${project_name}.orm_classes'
% endif
% if utils_py.check_need_mem_db(root) or utils_py.check_need_local_db(root):
local ok, datas = pcall(require, '${project_name}.datas')
if not ok then
    datas = nil  -- 如果没有datas配置，证明当前组件不需要datas，仅打开数据库
end
% endif

% for intf, intf_data in root['intf_imports'].items():
local ${intf}Types = require '${project_name}.json_types.${intf}'
% endfor

% for cls, cls_data in root['class_require'].items():
${mdb_obj.render(cls, cls_data['data'], root['class_require'])}
% endfor

% if root['path_level'] == 2:
local model = require 'class.model'
% else:
local model = require '${project_name}.class.model'
% endif

## 如果是子目录下的扩展，则不启动服务
% if root['path_level'] == 2:
local ${ClassName} = class(app_base.Service)
% else:
local ${ClassName} = class()
% endif

% if has_default:
${default_intf.add_subs(ClassName)}
% endif
${ClassName}.package = '${root['package']}'

% for rpc in root['methods']:
    %if rpc['default'] != '' and not rpc['override']:
<% default_path = ClassName +'.'+ rpc['intf_class'] + 'Default' %>
require '${project_name}.json_types.${rpc['intf_class']}Default'
${default_intf.render(default_path, ClassName, rpc['intf_class'] + "Default", rpc['interface'] + ".Default")}
    %endif
% endfor
## 动态对象生成创建接口,以便非CSR场景创建对象时使用
% for cls, cls_data in root['class_require'].items():
    % if render_utils.is_dynamic_obj(cls_data['path']):

function ${ClassName}:Create${cls}(${", ".join(render_utils.get_path_params(render_utils.get_path(cls, root['class_require'])))}, prop_setting_cb)
    local path = ${render_utils.make_path(render_utils.get_path(cls, root['class_require']))}
    return object_manage.create_object("${cls}", path, path, prop_setting_cb)
end
    % else:
% if version >= 15:

function ${ClassName}:Create${cls}(prop_setting_cb)
    return object_manage.create_object("${cls}", '${cls}_0', ${render_utils.make_path(render_utils.get_path(cls, root['class_require']))}, prop_setting_cb)
end
% endif
    % endif
%endfor

## 生成注册回调的接口，增加参数校验
% for rpc in root['methods']:
<% class_intf = rpc['class'] + '_' + rpc['intf_class'] %>
function ${ClassName}:Impl${rpc['name']}(cb)
    model.Impl${rpc['name']}(cb)
end
% endfor

% if version >= 9:
% for method, _ in root.get('private_class_require', {}).get('private', {}).get('data', {}).get('methods', {}).items():
function ${ClassName}:Impl${method}(cb)
    model.Impl${method}(cb)
end

function ${ClassName}:${method}(...)
    return model.${method}(...)
end

% endfor
% endif
## 生成发送信号的接口
% for signal in root['signals']:
<% params = render_utils.params(signal['signature'])%>
  % if ':' in signal['path']:
---@param mdb_object object
  % endif
  % for p in render_utils.props(signal['signature']): ## 生成参数注释
---@param ${p['name']} ${utils_py.do_type_to_lua(p['type'], p['repeated'])}
  % endfor
function ${ClassName}:${signal['name']}(${'mdb_object,' if (':' in signal['path']) else ''}${params})
    self.bus:signal(${'mdb_object.path' if (':' in signal['path']) else ('"'+signal['path']+'"')}, '${signal['interface']}', '${signal['signal_name']}', 'a{ss}${utils_py.do_service_types_to_dbus(root, signal['signature'][1:])}', context.get_context() or {}${"" if params == '' else ", "}${params})
end

% endfor

## 适配订阅的片段复用
function ${ClassName}:get_bus()
    return self.bus
end

% if root['has_ipmi_cmd']:
function ${ClassName}:register_ipmi_cmd(ipmi_cmd, cb)
    self.ipmi_cmds[ipmi_cmd.name] = ipmi.register_ipmi_cmd(self.bus, self.service_name, ipmi_cmd, cb or self[ipmi_cmd.name])
end

function ${ClassName}:unregister_ipmi_cmd(ipmi_cmd)
    local cmd_obj = self.ipmi_cmds[ipmi_cmd.name]
    if not cmd_obj then
        return
    end

    cmd_obj:unregister()
    self.ipmi_cmds[ipmi_cmd.name] = nil
end
% endif

% if root['path_level'] == 2:
function ${ClassName}:ctor()
% else:
function ${ClassName}:ctor(bus)
    self.bus = bus
% endif
% if root['has_ipmi_cmd']:
    self.ipmi_cmds = {}
% endif
    self.signal_slots = {}
    self.name = self.name or ${ClassName}.package
  % if utils_py.check_need_mem_db(root):
    self.db = open_db(':memory:', datas)
  % endif
  % if root['path_level'] == 2:
    % if utils_py.check_local_poweroff_db(root):
    self.local_db = open_local_db(app_base.Service:get_local_db_path(self.name) .. '/${project_name}.db', datas, 'poweroff')
    % endif
  % endif
  % if utils_py.check_local_reset_db(root) or utils_py.check_local_temporary_db(root):
    if skynet.getenv('TEST_DATA_DIR') then
    % if utils_py.check_local_reset_db(root):
        self.reset_local_db = open_local_db(skynet.getenv('TEST_DATA_DIR')..'/${project_name}_reset.db', datas, "reset")
    % endif
    % if utils_py.check_local_temporary_db(root):
        self.temporary_local_db = open_local_db(skynet.getenv('TEST_DATA_DIR')..'/${project_name}_temp.db', datas, "temporary")
    % endif
    else
    % if utils_py.check_local_reset_db(root):
        self.reset_local_db = open_local_db('/opt/bmc/pram/persistence.local/${project_name}.db', datas, "reset")
    % endif
    % if utils_py.check_local_temporary_db(root):
        self.temporary_local_db = open_local_db('/dev/shm/persistence.local/${project_name}.db', datas, "temporary")
    % endif
    end
  % endif

  % if utils_py.check_need_mem_db(root):
    orm_classes.init(self.db)
  % endif
  % if root['path_level'] == 2:
    self.bus:request_name(app_base.Service.get_service_name(self.name))
  % endif
    model.init(self.bus)
    ${ClassName}.bus = self.bus
end

% if root['path_level'] == 2:
function ${ClassName}:pre_init()
    ${ClassName}.super.pre_init(self)
    % if utils_py.check_remote_per(root):
    self.persist = persist_client.new(self.bus, self.db, self, ${render_utils.get_not_recover_tables(root)})
    object_manage.set_persist_client(self.persist)
    % endif
end
% endif

## servie初始化
function ${ClassName}:init()
% if root['path_level'] == 2:
    ${ClassName}.super.init(self)
%endif
% if has_default:
    self:SubscribeAll()
%endif
% if version < 15:
% for cls, cls_data in root['class_require'].items():## 非动态的对象初始化时就可以上树
    % if not render_utils.is_dynamic_obj(cls_data['path']):
    object_manage.create_object("${cls}", ${render_utils.make_path(render_utils.get_path(cls, root['class_require']))}, ${render_utils.make_path(render_utils.get_path(cls, root['class_require']))}, function(obj)
        obj.ObjectName = '${cls}_0'
    end)
    % endif
%endfor
% endif
% for rpc in root['methods']:
    %if not rpc['override'] :
    self:Impl${rpc['name']}(function(obj, ctx, ...)
        return self:Get${rpc['default']}Object():${rpc['func_name']}_PACKED(ctx, obj.path,...):unpack()
    end)
    %endif
% endfor
end

return ${ClassName}
% else:
${make_header('lua')}
<%namespace name="imports" file="utils/imports.mako"/>
<%namespace name="default_intf" file="utils/default_intf.lua.mako"/>
<%namespace name="mdb_obj" file= "utils/mdb_obj.lua.mako"/>
<% ClassName = root['package'] + '_service' %>

% if root['path_level'] == 2:
local app_base = require 'mc.service_app_base'
% endif
local class = require 'mc.class'
local mdb = require 'mc.mdb'
% if utils_py.check_remote_per(root):
local object_manage = require 'mc.mdb.object_manage'
local persist_client = require 'persistence.persist_client_lib'
% endif
local context = require 'mc.context'

% for intf, intf_data in root['intf_imports'].items():
local ${intf}Types = require '${project_name}.json_types.${intf}'
% endfor

% for cls, cls_data in root['class_require'].items():
${mdb_obj.render(cls, cls_data['data'], root['class_require'])}
% endfor

local cls_mng = require 'mc.class_mgnt'
% if root['path_level'] == 2:
local model = require 'class.model'
% else:
local model = require '${project_name}.class.model'
% endif

% if utils_py.check_local_poweroff_db(root) or utils_py.check_local_reset_db(root) or utils_py.check_local_temporary_db(root):
local open_local_db = require '${project_name}.local_db'
% endif
% if utils_py.check_db_open(root['package']):
local open_db = require '${project_name}.db'
local orm_classes = require '${project_name}.orm_classes'
local ok, datas = pcall(require, '${project_name}.datas')
if not ok then
    -- 如果没有datas配置，证明当前组件不需要datas，仅打开数据库
    datas = nil
end
% endif

## 如果是子目录下的扩展，则不启动服务
% if root['path_level'] == 2:
local ${ClassName} = class(app_base.Service)
% else:
local ${ClassName} = class()
% endif

${default_intf.add_subs(ClassName)}
${ClassName}.package = '${root['package']}'

% for rpc in root['methods']:
    %if rpc['default'] != '' and not rpc['override']:
<% default_path = ClassName +'.'+ rpc['intf_class'] + 'Default' %>
require '${project_name}.json_types.${rpc['intf_class']}Default'
${default_intf.render(default_path, ClassName, rpc['intf_class'] + "Default", rpc['interface'] + ".Default")}
    %endif
% endfor
## 动态对象生成创建接口,以便非CSR场景创建对象时使用
% for cls, cls_data in root['class_require'].items():
    % if render_utils.is_dynamic_obj(cls_data['path']):
function ${ClassName}:Create${cls}(${", ".join(render_utils.get_path_params(render_utils.get_path(cls, root['class_require'])))}, prop_setting_cb)
    local path = ${render_utils.make_path(render_utils.get_path(cls, root['class_require']))}
    local object = cls_mng("${cls}").new(path)
    object:create_mdb_objects(path)
    if prop_setting_cb then
        prop_setting_cb(object)
    end
% if root['path_level'] == 2 and utils_py.check_remote_per(root):
    object:assign_persistence_props(self.persist)
% endif
    object:register_mdb_objects()
    return object
end
    % endif
%endfor

## 生成注册回调的接口，增加参数校验
% for rpc in root['methods']:
<% class_intf = rpc['class'] + '_' + rpc['intf_class'] %>
function ${ClassName}:Impl${rpc['name']}(cb)
    model.Impl${rpc['name']}(cb)
end
% endfor

## 生成发送信号的接口
% for signal in root['signals']:
<% params = render_utils.params(signal['signature'])%>
  % if ':' in signal['path']:
---@param mdb_object object
  % endif
  % for p in render_utils.props(signal['signature']): ## 生成参数注释
---@param ${p['name']} ${utils_py.do_type_to_lua(p['type'], p['repeated'])}
  % endfor
function ${ClassName}:${signal['name']}(${'mdb_object,' if (':' in signal['path']) else ''}${params})
    self.bus:signal(${'mdb_object.path' if (':' in signal['path']) else ('"'+signal['path']+'"')}, '${signal['interface']}', '${signal['signal_name']}', 'a{ss}${utils_py.do_service_types_to_dbus(root, signal['signature'][1:])}', context.get_context() or {}${"" if params == '' else ", "}${params})
end

% endfor

## 适配订阅的片段复用
function ${ClassName}:get_bus()
    return self.bus
end

% if root['path_level'] == 2:
function ${ClassName}:ctor()
% else:
function ${ClassName}:ctor(bus)
    self.bus = bus
% endif
    if not self.name then
        self.name = ${ClassName}.package
    end
    self.signal_slots = {}
    % if 'Security' in root['package']:
    local skynet = require 'skynet'
    self.db = open_db(skynet.getenv('SECURITY_DB'), datas)
    % elif utils_py.check_db_open(root['package']):
    % if root['path_level'] == 2:
    % if utils_py.check_local_poweroff_db(root):
        self.local_db = open_local_db(app_base.Service:get_local_db_path(self.name) .. '/${project_name}.db', datas, 'poweroff')
    % endif
    % endif
    % if utils_py.check_local_reset_db(root):
    local skynet = require 'skynet'
    if skynet.getenv('TEST_DATA_DIR') then
        self.reset_local_db = open_local_db(skynet.getenv('TEST_DATA_DIR')..'/${project_name}_reset.db', datas, "reset")
    else
        self.reset_local_db = open_local_db('/opt/bmc/pram/persistence.local/${project_name}.db', datas, "reset")
    end
    % endif
    % if utils_py.check_local_temporary_db(root):
    local skynet = require 'skynet'
    if skynet.getenv('TEST_DATA_DIR') then
        self.temporary_local_db = open_local_db(skynet.getenv('TEST_DATA_DIR')..'/${project_name}_temp.db', datas, "temporary")
    else
        self.temporary_local_db = open_local_db('/dev/shm/persistence.local/${project_name}.db', datas, "temporary")
    end
    % endif
    self.db = open_db(':memory:', datas)
    orm_classes.init(self.db)
    % if root['path_level'] == 2:
    self.bus:request_name(app_base.Service.get_service_name(self.name))
    % endif
    % endif

    model.init(self.bus)

    ${ClassName}.bus = self.bus
end

% if root['path_level'] == 2:
% if utils_py.check_db_open(root['package']):
function ${ClassName}:pre_init()
    if ${ClassName}.super.pre_init then
        ${ClassName}.super.pre_init(self)
    end
% if utils_py.check_remote_per(root):
    self.persist = persist_client.new(self.bus, self.db, self, ${render_utils.get_not_recover_tables(root)})
    object_manage.set_persist_client(self.persist)
% endif
end
% endif
% endif

## servie初始化
function ${ClassName}:init()
% if root['path_level'] == 2:
    ${ClassName}.super.init(self)
%endif
    self:SubscribeAll()
% for cls, cls_data in root['class_require'].items():## 非动态的对象初始化时就可以上树
    % if not render_utils.is_dynamic_obj(cls_data['path']):
    local object = cls_mng("${cls}").new(${render_utils.make_path(cls_data['path'])})
    object:create_mdb_objects(${render_utils.make_path(cls_data['path'])})
    object.ObjectName = '${cls}_0'
% if root['path_level'] == 2 and utils_py.check_remote_per(root):
    object:assign_persistence_props(self.persist)
% endif
    object:register_mdb_objects()
    % endif
%endfor

% for rpc in root['methods']:
    %if not rpc['override'] :
    self:Impl${rpc['name']}(function(obj, ctx, ...)
        return self:Get${rpc['default']}Object():${rpc['func_name']}_PACKED(ctx, obj.path,...):unpack()
    end)
    %endif
% endfor

end

return ${ClassName}
%endif