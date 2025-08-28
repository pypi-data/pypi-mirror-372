${make_header('lua')}
<%
messages = [msg for msg in root['data'] if (msg['type'] != 'Enum' and 'interface' not in msg['options']) ]
enums = [msg for msg in root['data'] if msg['type'] == 'Enum']
%>
% if len(messages) > 0 or len(enums) > 0:
local validate = require 'mc.validate'
local utils = require 'mc.utils'
% endif
% if len(enums) > 0:
local create_enum_type = require 'mc.enum'
% endif
<%namespace name="message" file="utils/message.mako"/>
<%namespace name="imports" file="utils/imports.mako"/>
<%namespace name="enum" file="utils/enum.mako"/>
${imports.render(root)}

% if len(messages) > 0 or len(enums) > 0:
local msg = {}
local defs = {}
% endif

% for msg in enums:
${enum.render(msg, 'create_enum_type')}
${'defs' if msg['package'] == 'defs' else 'msg'}.${msg['name']} = E${msg['name']}

% endfor

% for msg in messages:
${message.render(msg)}

${'defs' if msg['package'] == 'defs' else 'msg'}.${msg['name']} = T${msg['name']}
% endfor

local ${root['package']} = {}

local mdb = require 'mc.mdb'

% for msg in root['data']:
  % if render_utils.has_interface(msg):

---@class ${msg['name']}: Table
    % for p in msg['properties']:
---@field ${p['name']} ${utils_py.do_type_to_lua(p['type'], p['repeated'])}
    % endfor
${root['package']}.${msg['name']} = mdb.register_interface('${msg['options']['interface']}', {
    % for p in msg['properties']:
      ${p['name']} = {'${utils_py.do_type_to_dbus(p['type'], p['repeated'])}', ${render_utils.get_flags(p)}, ${render_utils.readonly_flag(p)}, ${render_utils.default(p)}},
    % endfor
    % if len(render_utils.make_methods(root, msg['options']['interface'])) == 0 and not render_utils.has_signals(msg):
  }, {}, {})
    % elif len(render_utils.make_methods(root, msg['options']['interface'])) > 0 :
  }, {
      % for p in render_utils.make_methods(root, msg['options']['interface']):
      ${p['name']} = {'a{ss}${utils_py.do_service_types_to_dbus(root, p['req'][1:])}', '${utils_py.do_service_types_to_dbus(root, p['rsp'][1:])}', ${render_utils.get_json_req(p)}, ${render_utils.get_json_rsp(p)}},
      % endfor
      % if render_utils.has_signals(msg):
  }, {
        % for p in msg['nested_type']:
      ${p['name']} = '${utils_py.do_types_to_dbus(p)}',
        % endfor
  })
      % else :
  }, {})
      % endif
    % else :
  }, {}, {

    }
      % endif
  % endif
% endfor
return ${root['package']}