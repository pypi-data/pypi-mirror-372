${make_header('lua')}
local privilege = require 'mc.privilege'
% if render_utils.get_features(root):
require 'mc.plugin.loader'.load()
  % for feature in render_utils.get_features(root):
local ${feature} = require '${project_name}.features.${feature}'.get_instance()
  % endfor
% endif

${render_utils.render_types(project_name, root)}

local classes = {}

% for (class_name, msg) in root.items():

classes.${class_name} = {
  % if render_utils.has_table_name(msg):
    ['table_name'] = '${msg['tableName']}',
  % endif
  % if render_utils.is_enable_orm(msg):
    ['enable_orm'] = true,
  % endif
  % if render_utils.has_alias(msg):
    ['alias_map'] = ${render_utils.get_alias_map(msg)},
  % endif
  % if render_utils.has_prop_configs(msg):
    ['prop_configs'] = ${render_utils.get_prop_configs(class_name, msg)},
  % endif
  % if render_utils.has_mdb_prop_configs(msg):
    ['mdb_prop_configs'] = ${render_utils.get_mdb_prop_configs(msg)},
  % endif
  % if render_utils.has_private_method_configs(msg):
    ['method_configs'] = ${render_utils.get_private_method_configs(class_name, msg)},
  % endif
  % if render_utils.has_mdb_method_configs(msg):
    ['mdb_method_configs'] = ${render_utils.get_mdb_method_configs(msg)},
  % endif
  % if render_utils.has_mdb_signal_configs(msg):
    ['mdb_signal_configs'] = ${render_utils.get_mdb_signal_configs(msg)},
  % endif
  % if render_utils.has_path(msg):
    ['path'] = ${render_utils.get_full_path(root, msg)},
  % endif
  % if render_utils.has_interfaces(msg):
    ['interface_types'] = ${render_utils.get_interface_types(msg)},
  % endif
}

% endfor

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

return {classes = classes${", block_io_classes = block_io_classes" if render_utils.has_block_io(root) else ""}}