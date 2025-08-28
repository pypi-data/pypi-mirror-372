${make_header('lua')}
<%namespace name="imports" file="../../../templates/apps/utils/imports.mako"/>
<%namespace name="default_intf" file="../../../templates/apps/utils/default_intf.lua.mako"/>
<%namespace name="mdb_obj" file= "utils/mdb_obj.lua.mako"/>
<% has_signal = root['signals']%>
<% has_mdb = any('path' in cls_data for cls, cls_data in root['class_require'].items())%>
<% has_default = any((rpc['default'] != '' and not rpc['override']) for rpc in root['methods'])%>
<% ClassName = root['package'] + '_service' %>

% if root['has_ipmi_cmd']:
local ipmi = require 'ipmi'
% endif
% if has_default:
local mdb = require 'mc.mdb'
% endif
local class = require 'mc.class'
% if has_signal:
local context = require 'mc.context'
% endif
local c = require 'mc.class_mgnt'
local bootstrap = require 'mc.bootstrap'
% if (root['path_level'] == 2 and utils_py.check_db_open(root['package']) and utils_py.check_remote_per(root)) or root['class_require']:
local object_manage = require 'mc.mdb.object_manage'
% endif
% if root['path_level'] == 2 and utils_py.check_db_open(root['package']) and utils_py.check_remote_per(root):
local persist_client = require 'persistence.persist_client_lib'
% endif

local class_data = {}

% for cls, cls_data in root['class_require'].items():
    class_data.${cls} = {${mdb_obj.render(cls, cls_data['data'], root['class_require'])}}
% endfor

% if root['path_level'] == 2:
local ${ClassName} = class(bootstrap.Service)
% else:
local ${ClassName} = class(bootstrap.Attach)
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

function ${ClassName}:Create${cls}(prop_setting_cb)
    return object_manage.create_object("${cls}", '${cls}_0', ${render_utils.make_path(render_utils.get_path(cls, root['class_require']))}, prop_setting_cb)
end
    % endif
%endfor

## 生成注册回调的接口，增加参数校验
% for rpc in root['methods']:
<% class_intf = rpc['class'] + '_' + rpc['intf_class'] %>
% if rpc['interface'] != "bmc.kepler.Object.Properties":
function ${ClassName}:Impl${rpc['name']}(cb)
    c("${rpc['class']}"):_implement("${rpc['name']}", "${rpc['interface']}", "${rpc['func_name']}", cb)
end
% endif
% endfor

% for method, _ in root.get('private_class_require', {}).get('private', {}).get('data', {}).get('methods', {}).items():
function ${ClassName}:Impl${method}(cb)
    c('private'):_implement("${method}", nil, "${method}", cb)
end

function ${ClassName}:${method}(...)
    return c('private'):_call("${method}", ...)
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

function ${ClassName}:ctor(${"" if root['path_level'] == 2 else "bus"})
  % if utils_py.has_db(root):
    self.db_types = ${utils_py.get_db_types(root)}
  % endif
    self.class_data = class_data
    self.name = '${project_name}'
end

% if root['path_level'] == 2:
function ${ClassName}:pre_init()
    ${ClassName}.super.pre_init(self)
    % if utils_py.check_remote_per(root):
    self.persist = persist_client.new(self.bus, self.db, self, ${render_utils.get_not_recover_tables(root)})
    % endif
end
% endif

## service初始化
function ${ClassName}:init()
% if root['path_level'] == 2:
    ${ClassName}.super.init(self)
%endif
% if has_default:
    self:SubscribeAll()
%endif
% for rpc in root['methods']:
    %if not rpc['override'] :
    self:Impl${rpc['name']}(function(obj, ctx, ...)
        return self:Get${rpc['default']}Object():${rpc['func_name']}_PACKED(ctx, obj.path,...):unpack()
    end)
    %endif
% endfor
end

return ${ClassName}