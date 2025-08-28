## 生成所有rpc接口
<%def name="get_obj(rpc)">
% if rpc['path'] != '*': ## 非虚方法和收集类方法，直接远程调用
  % if 'paths' in rpc and not rpc['virtual']:
    %if not rpc['retry']:
    mdb.get_object(self:get_bus(), ${render_utils.make_path_with_params(rpc['full_path'])}, '${rpc['interface']}')
    %else:
    mdb.try_get_object(self:get_bus(), ${render_utils.get_object_path(rpc['full_path'])}, '${rpc['interface']}')
    %endif
  % else:
    self:Get${rpc['class']}${rpc['intf_class']}Object(${render_utils.get_path_arg(rpc["full_path"], False)})
  % endif
% elif not rpc['virtual']:
    mdb.get_object(self:get_bus(), ${render_utils.make_path_with_params(rpc['full_path'])}, "${rpc['interface']}")
% else :
    self:Get${rpc['intf_class']}Object()
% endif
</%def>
${make_header('lua')}
<% has_signal = root['signals']%>
<% has_interface = root['interfaces']%>
<% has_definite_path = any((rpc['path'] != '*') for rpc in root['interfaces'])%>
<% has_virtual = any((rpc['path'] == '*' and rpc['virtual']) for rpc in root['interfaces'])%>
<% has_implement = any((rpc['implement'] != '') for rpc in root['interfaces'])%>
<% has_non_virtual = any(((rpc['path'] == '*' or ((render_utils.get_path_params(rpc["full_path"]) or 'paths' in rpc))) and not rpc['virtual'] and rpc['implement'] == '') for rpc in root['interfaces'])%>
% if has_definite_path or has_implement:
local mdb = require 'mc.mdb'
% endif
local class = require 'mc.class'
local app_base = require 'mc.client_app_base'
% if has_signal or has_non_virtual:
local mdb_service = require 'mc.mdb.mdb_service'
% endif
% if has_interface:
local subscribe_signal = require 'mc.mdb.subscribe_signal'
% endif
% if has_signal:
local org_freedesktop_dbus = require 'sd_bus.org_freedesktop_dbus'
% endif

% if has_signal:
local match_rule = org_freedesktop_dbus.MatchRule
% endif
% if has_virtual:
local get_virtual_interface_object = mdb_service.get_virtual_interface_object
% endif
% if has_non_virtual:
local get_non_virtual_interface_objects = mdb_service.get_non_virtual_interface_objects
local foreach_non_virtual_interface_objects = mdb_service.foreach_non_virtual_interface_objects
% endif

## 生成对接口的依赖
% for intf, intf_data in root['intf_imports'].items():
  % if intf_data['interface'].startswith('bmc.dev.'):
local ${intf} = require '${project_name}.device_types.${intf}'
  %else:
local ${intf} = require '${project_name}.json_types.${intf}'
  % endif
% endfor

<%namespace name="default_intf" file="../../../templates/apps/utils/default_intf.lua.mako"/>
<%namespace name="imports" file="../../../templates/apps/utils/imports.mako"/>
${imports.render(root)}

<%
ClassName = root['package'] + '_client'
%>
---@class ${ClassName}: BasicClient
local ${ClassName} = class(app_base.Client)

% if has_implement:
${default_intf.add_subs(ClassName)}
% endif
## 收集复写类方法订阅接口
% for rpc in root['interfaces']:
  % if rpc['path'] == '*' and rpc['virtual']:

function ${ClassName}:Get${rpc['intf_class']}Object()
  return get_virtual_interface_object(self:get_bus(), '${rpc['interface']}')
end
  % endif
%endfor
## 生成收集类client订阅接口
% for rpc in root['interfaces']:
  %if rpc['path'] == '*' and not rpc['virtual'] and rpc['implement'] == '':

function ${ClassName}:Get${rpc['intf_class']}Objects()
  return get_non_virtual_interface_objects(self:get_bus(), '${rpc['interface']}', ${'true' if rpc['retry'] else 'false'})
end

function ${ClassName}:Foreach${rpc['intf_class']}Objects(cb)
  return foreach_non_virtual_interface_objects(self:get_bus(), '${rpc['interface']}', cb, ${'true' if rpc['retry'] else 'false'})
end
  % endif
%endfor

## 生成默认对象的订阅和访问接口
% for rpc in root['interfaces']:
  %if rpc['implement'] != '' :
    <% default_path = ClassName +'.'+ rpc['intf_class'] +"_default" %>
${default_intf.render(default_path, ClassName, rpc['intf_class'], rpc['interface'])}
  % endif
%endfor

% for rpc in root['interfaces']:
  % if 'paths' in rpc and not rpc['virtual']:
function ${ClassName}:MutipleGet${rpc['intf_class']}Objects(${render_utils.get_path_arg(rpc["paths"], False)})
  local paths_namespace = ${render_utils.get_paths_namespace(rpc["paths"])}
  return get_non_virtual_interface_objects(self:get_bus(), '${rpc['interface']}', ${'true' if rpc['retry'] else 'false'}, paths_namespace)
end

function ${ClassName}:MutipleForeach${rpc['intf_class']}Objects(cb${render_utils.get_path_arg(rpc["paths"])})
  local paths_namespace = ${render_utils.get_paths_namespace(rpc["paths"])}
  return foreach_non_virtual_interface_objects(self:get_bus(), '${rpc['interface']}', cb, ${'true' if rpc['retry'] else 'false'}, paths_namespace)
end

% if rpc['dep_properties']:
function ${ClassName}:MutipleOn${rpc['intf_class']}PropertiesChanged(cb${render_utils.get_path_arg(rpc["paths"])})
  local paths_namespace = ${render_utils.get_paths_namespace(rpc["paths"])}
  self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_properties_changed(self:get_bus(), paths_namespace, cb, '${rpc['interface']}'${render_utils.get_dep_properties(rpc["dep_properties"])})
end
%endif

function ${ClassName}:MutipleOn${rpc['intf_class']}InterfacesAdded(cb${render_utils.get_path_arg(rpc["paths"])})
  local paths_namespace = ${render_utils.get_paths_namespace(rpc["paths"])}
  self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_interfaces_added(self:get_bus(), paths_namespace, cb, '${rpc['interface']}')
end

function ${ClassName}:MutipleOn${rpc['intf_class']}InterfacesRemoved(cb${render_utils.get_path_arg(rpc["paths"])})
  local paths_namespace = ${render_utils.get_paths_namespace(rpc["paths"])}
  self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_interfaces_removed(self:get_bus(), paths_namespace, cb, '${rpc['interface']}')
end

    <% continue %>
  % endif
  % if rpc['path'] != '*':
function ${ClassName}:Get${rpc['name']}Object(${render_utils.get_path_arg(rpc["full_path"], False)})
    %if not rpc['retry']:
return mdb.get_object(self:get_bus(), ${render_utils.make_path_with_params(rpc['full_path'])}, '${rpc['interface']}')
    %else:
return mdb.try_get_object(self:get_bus(), ${render_utils.get_object_path(rpc['full_path'])}, '${rpc['interface']}')
    %endif
end

  % if render_utils.get_path_params(rpc["full_path"]):
function ${ClassName}:Get${rpc['intf_class']}Objects()
  return get_non_virtual_interface_objects(self:get_bus(), '${rpc['interface']}', ${'true' if rpc['retry'] else 'false'}, ${render_utils.get_path_patterns([rpc["full_path"]])})
end

function ${ClassName}:Foreach${rpc['intf_class']}Objects(cb)
  return foreach_non_virtual_interface_objects(self:get_bus(), '${rpc['interface']}', cb, ${'true' if rpc['retry'] else 'false'}, ${render_utils.get_path_patterns([rpc["full_path"]])})
end
  %endif

% if rpc['dep_properties']:
function ${ClassName}:On${rpc['intf_class']}PropertiesChanged(cb${render_utils.get_path_arg(rpc["full_path"])})
    local path_namespace = ${render_utils.get_path_namespace(rpc['full_path'])}
    self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_properties_changed(self:get_bus(), path_namespace, cb, '${rpc['interface']}'${render_utils.get_dep_properties(rpc["dep_properties"])})
end
%endif

function ${ClassName}:On${rpc['intf_class']}InterfacesAdded(cb${render_utils.get_path_arg(rpc["full_path"])})
    local path_namespace = ${render_utils.get_path_namespace(rpc['full_path'])}
    self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_interfaces_added(self:get_bus(), path_namespace, cb, '${rpc['interface']}')
end

function ${ClassName}:On${rpc['intf_class']}InterfacesRemoved(cb${render_utils.get_path_arg(rpc["full_path"])})
    local path_namespace = ${render_utils.get_path_namespace(rpc['full_path'])}
    self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_interfaces_removed(self:get_bus(), path_namespace, cb, '${rpc['interface']}')
end

  % else :
% if rpc['dep_properties']:
function ${ClassName}:On${rpc['intf_class']}PropertiesChanged(cb)
    self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_properties_changed(self:get_bus(), '/bmc', cb, '${rpc['interface']}'${render_utils.get_dep_properties(rpc["dep_properties"])})
end
%endif

function ${ClassName}:On${rpc['intf_class']}InterfacesAdded(cb)
    self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_interfaces_added(self:get_bus(), '/bmc', cb, '${rpc['interface']}')
end

function ${ClassName}:On${rpc['intf_class']}InterfacesRemoved(cb)
    self.signal_slots[#self.signal_slots + 1] = subscribe_signal.on_interfaces_removed(self:get_bus(), '/bmc', cb, '${rpc['interface']}')
end

  % endif
%endfor
% for rpc in root['methods']:
  %if rpc['path'] == '*'  and not rpc['virtual']:
    <% continue %>
  % endif
  % for p in render_utils.props(rpc['req']): ## 生成参数注释
---@param ${p['name']} ${utils_py.do_type_to_lua(p['type'], p['repeated'])}
  % endfor
  % if render_utils.rsp_message(rpc) != 'nil': ## 生成返回值注释
---@return ${render_utils.rsp_message(rpc)}
  % endif
  % if len(render_utils.params(rpc['req'])) == 0: ## 区分参数个数生成参数, 没有参数的b
function ${ClassName}:${rpc['name']}(ctx${render_utils.get_path_arg(rpc["full_path"])})
  local obj = ${get_obj(rpc)}
  return ${render_utils.rsp_message(rpc)}.new(obj:${rpc['func_name']}(ctx))
end

function ${ClassName}:P${rpc['name']}(ctx${render_utils.get_path_arg(rpc["full_path"])})
  return pcall(self.${rpc['name']}, self, ctx${render_utils.get_path_arg(rpc["full_path"])})
end

  % else:  ## 有参数的
function ${ClassName}:${rpc['name']}(ctx${render_utils.get_path_arg(rpc["full_path"])}, ${render_utils.params(rpc['req'])})
  local req = ${render_utils.req_message(rpc)}.new(${render_utils.params(rpc['req'])}):validate()
  local obj = ${get_obj(rpc)}return ${render_utils.rsp_message(rpc)}.new(obj:${rpc['func_name']}(ctx, req:unpack(true)))
end

function ${ClassName}:P${rpc['name']}(ctx${render_utils.get_path_arg(rpc["full_path"])}, ${render_utils.params(rpc['req'])})
  return pcall(self.${rpc['name']}, self, ctx${render_utils.get_path_arg(rpc["full_path"])}, ${render_utils.params(rpc['req'])})
end

  % endif
% endfor
## 生成信号订阅接口
% for signal in root['signals']:
function ${ClassName}:Subscribe${signal['name']}(cb)
  local sig = match_rule.signal('${signal['signal_name']}', '${signal['interface']}')${'' if signal['path'] == '*' else (':with_path("' +signal['path']+'")')}
  self.signal_slots[#self.signal_slots+1] = subscribe_signal.subscribe(self:get_bus(), sig, cb)
end

% endfor
function ${ClassName}:ctor()
  self.signal_slots = {}
end

---@type ${ClassName}
return ${ClassName}.new('${root['package']}')