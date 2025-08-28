% if version >= 4:
${make_header('lua')}
local mdb = require 'mc.mdb'
local class = require 'mc.class_mgnt'
local privilege = require 'mc.privilege'
% if version >= 9 and render_utils.get_features(root):
require 'mc.plugin.loader'.load()
  % for feature in render_utils.get_features(root):
local ${feature} = require '${project_name}.features.${feature}'.get_instance()
  % endfor
% endif

${render_utils.render_types(project_name, root)}

% for (class_name, msg) in root.items():

<% msg = render_utils.remove_description(msg) %>

% if version >= 9:
  % if class_name == 'private':
    <% continue %>
  % endif
% endif
local ${class_name} = {
  % if render_utils.has_table_name(msg):
    ['table_name'] = '${msg['tableName']}',
  % endif
  % if render_utils.has_alias(msg):
    ['alias_map'] = ${render_utils.get_alias_map(msg)},
  % endif
  % if render_utils.has_prop_configs(msg):
    ['prop_configs'] = ${render_utils.get_prop_configs(class_name, msg)},
  % endif
  % if render_utils.has_properties(msg):
    ['default_props'] = ${render_utils.get_default_props(class_name, msg)},
  % endif
  % if render_utils.has_mdb_prop_configs(msg):
    ['mdb_prop_configs'] = ${render_utils.get_mdb_prop_configs(msg)},
  % endif
  % if render_utils.has_mdb_method_configs(msg):
    ['mdb_method_configs'] = ${render_utils.get_mdb_method_configs(msg)},
  % endif
  % if render_utils.has_mdb_signal_configs(msg):
    ['mdb_signal_configs'] = ${render_utils.get_mdb_signal_configs(msg)},
  % endif
  % if render_utils.has_mdb_classes(msg):
    ['mdb_classes'] = ${render_utils.get_mdb_classes(root, msg)},
  % endif
  % if render_utils.has_new_mdb_objects(msg):
    ['new_mdb_objects'] = ${render_utils.get_new_mdb_objects(msg)},
  % endif
}

% endfor
local M = {}

% if render_utils.has_block_io(root):
M.block_io_classes = {
  % for (class_name, msg) in root.items():
    % if render_utils.has_path(msg):
      % for (interface, intf_msg) in msg['interfaces'].items():
        % if interface == 'bmc.kepler.Chip.BlockIO':
    '${class_name}',
        % endif
      %endfor
    % endif
  % endfor
}
% endif

function M.init(bus)
% for (class_name, msg) in root.items():
    % if class_name != 'private':
    class('${class_name}', ${class_name}):set_bus(bus)
    % endif
% endfor
end
% for (class_name, msg) in root.items():
  % if render_utils.has_path(msg):
    % for (interface, intf_msg) in msg['interfaces'].items():
      % if render_utils.has_methods(intf_msg):

        % for (method, method_config) in intf_msg['methods'].items():
-- The callback needs to be registered during app initialization
function M.Impl${class_name}${render_utils.get_intf_name(interface, intf_msg)}${method}(cb)
    class('${class_name}')['${interface}'].${method} = function(obj, ctx, ...)
          % if version >= 9 and "featureTag" in method_config:
        ${method_config["featureTag"]}:set_default_callback("${class_name}${render_utils.get_intf_name(interface, intf_msg)}${method}", cb)
          % endif
        local req = ${render_utils.get_intf_type(render_utils.get_intf_name(interface, intf_msg))}.${method}Req.new(...):validate(nil, nil, true)
          % if version >= 9 and "featureTag" in method_config:
        local rsp = ${render_utils.get_intf_type(render_utils.get_intf_name(interface, intf_msg))}.${method}Rsp.new(${method_config["featureTag"]}:${class_name}${render_utils.get_intf_name(interface, intf_msg)}${method}(obj, ctx, req:unpack())):validate()
          % else:
        local rsp = ${render_utils.get_intf_type(render_utils.get_intf_name(interface, intf_msg))}.${method}Rsp.new(cb(obj, ctx, req:unpack())):validate()
          % endif
        return rsp:unpack(true)
    end
end

        %endfor
      % endif
    %endfor
  % endif
% endfor
% if version >= 9:
% for method, method_config in root.get("private", {}).get("methods", {}).items():
  % if "featureTag" in method_config:
-- The callback needs to be registered during app initialization
function M.Impl${method}(cb)
    ${method_config["featureTag"]}:set_default_callback("${method}", cb)
end

function M.${method}(...)
    local req = ${render_utils.get_class_type("private")}.${method}Req.new(...):validate(nil, nil, true)
    local rsp = ${render_utils.get_class_type("private")}.${method}Rsp.new(${method_config["featureTag"]}:${method}(req:unpack())):validate()
    return rsp:unpack(true)
end

  % endif
% endfor
% endif
return M
% else:
${make_header('lua')}
local mdb = require 'mc.mdb'
local utils = require 'mc.utils'
local logging = require 'mc.logging'
local class = require 'mc.class_mgnt'
local err = require 'validate.errors'
local privilege = require 'mc.privilege'

local get_table_node = utils.get_table_node

% for (class_name, msg) in root.items():
  % if render_utils.has_path(msg):
local ${class_name.lower()}_mdb_prop_configs =  ${render_utils.get_mdb_prop_configs(project_name, msg)}
  % else:
local ${class_name.lower()}_mdb_prop_configs = {}
  % endif

local ${class_name} = {
  % if render_utils.has_table_name(msg):  
    ['table_name'] = '${msg['tableName']}',
  % endif
    ['alias_map'] = ${render_utils.get_alias_map(msg)},
    ['prop_configs'] = ${render_utils.get_prop_configs(class_name, msg, project_name)},
    ['default_props'] = ${render_utils.get_default_props(project_name, class_name, msg)},
    ['mdb_prop_configs'] = ${class_name.lower()}_mdb_prop_configs,
    ['mdb_method_configs'] = ${render_utils.get_mdb_method_configs(msg)},
    ['mdb_signal_configs'] = ${render_utils.get_mdb_signal_configs(msg)},
    ['mdb_classes'] = ${render_utils.get_mdb_classes(root, msg)},
    % if render_utils.has_path(msg):
    ['new_mdb_objects'] = function(path)
      local objs = {} <% num = 0 %>
      % for (interface, intf_msg) in msg['interfaces'].items():
        % if num == 0:
        local obj_cls, params = mdb.match_interface(path, '${interface}')
        % else:
        obj_cls, params = mdb.match_interface(path, '${interface}')
        % endif
        if not obj_cls then <% intf_name = render_utils.get_intf_name(interface, intf_msg)%>
          % if use_frame_log:
          logging:mcf_warn('Not match interface, path:%s, interface:%s', path, '${interface}')
          % else:
          logging:warn('Not match interface, path:%s, interface:%s', path, '${interface}')
          % endif
        else
          local obj = obj_cls.new(table.unpack(params))
        % if render_utils.has_properties(intf_msg):
          % for (prop, prop_config) in intf_msg['properties'].items():
            obj["${prop}"] = ${render_utils.get_mdb_prop_default_value(project_name, intf_name, prop, prop_config)}
          % endfor
        % endif
          obj:access_control({
            % if 'privilege' in msg:
            path = ${render_utils.get_privilege(msg)},
            % endif
            % if 'privilege' in intf_msg:
            interface = ${render_utils.get_privilege(intf_msg)},
            % endif
            props = ${render_utils.get_property_privileges(intf_msg.get('properties', {}))},
            methods = ${render_utils.get_privileges(intf_msg.get('methods', {}))}
            }, 
            ${render_utils.get_readonlys(intf_msg.get('properties', {}))},
            require '${project_name}.json_types.${intf_name}')
        objs['${interface}'] = obj
        end<% num = num + 1 %>
      % endfor
      return objs
    end
  % else:
    ['new_mdb_objects'] = nil
  % endif
}

% endfor
local M = {}

% if render_utils.has_block_io(root):
M.block_io_classes = {
  % for (class_name, msg) in root.items():
    % if render_utils.has_path(msg):
      % for (interface, intf_msg) in msg['interfaces'].items():
        % if interface == 'bmc.kepler.Chip.BlockIO':
    '${class_name}',
        % endif
      %endfor
    % endif
  % endfor
}
% endif

function M.init(bus)
% for (class_name, msg) in root.items():
    class('${class_name}', ${class_name}):set_bus(bus)
% endfor
end
% for (class_name, msg) in root.items():
  % if render_utils.has_path(msg):
    % for (interface, intf_msg) in msg['interfaces'].items():
      % if render_utils.has_methods(intf_msg):

        % for (method, method_config) in intf_msg['methods'].items():
-- The callback needs to be registered during app initialization
function M.Impl${class_name}${render_utils.get_intf_name(interface, intf_msg)}${method}(cb)
    class('${class_name}')['${interface}'].${method} = function(obj, ctx, ...)
        local ${interface.split(".")[-1].lower()}_types = require "${project_name}.json_types.${render_utils.get_intf_name(interface, intf_msg)}"
        local req = ${interface.split(".")[-1].lower()}_types.${method}Req.new(...):validate(nil, nil, true)
        local rsp = ${interface.split(".")[-1].lower()}_types.${method}Rsp.new(cb(obj, ctx, req:unpack())):validate()
        return rsp:unpack(true)
    end
end

        %endfor
      % endif
    %endfor
  % endif

% endfor
return M
% endif