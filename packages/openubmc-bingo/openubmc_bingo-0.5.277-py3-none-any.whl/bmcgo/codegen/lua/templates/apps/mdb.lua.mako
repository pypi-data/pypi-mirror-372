${make_header('lua')}
<%
interface_package = {}
def fill_interface_package(value):
  interface_package[value] = true
  return ''
%>
% for msg in root['data']:
  % if render_utils.has_path(msg):
    % for p in msg['properties']:
      % if p['type'] not in interface_package:
local ${p['type']}Interface = require 'mdb.${p['options']['interface']}Interface'
      % endif
    % endfor
  % endif
% endfor

local childs = {}
% for (pkg, path) in render_utils.dependency(root):
  % if not path.endswith('/types/message'):
childs.${pkg} = require '${path.replace("/", ".")}'
  % endif
% endfor
local ${root['package']} = {childs = childs}

% if render_utils.has_msg(root):
local mdb = require 'mc.mdb'

  % for msg in root['data']:
    % if render_utils.has_path(msg):
local T${msg['name']} = mdb.register_object('${msg['options']['path']}', {
      % for p in msg['properties']:
        {name = '${p['name']}', interface = ${p['type']}Interface.${p['type']}},
      % endfor
    })
${root['package']}.${msg['name']}= T${msg['name']}

function T${msg['name']}:ctor(${", ".join(render_utils.get_path_params(msg['options']['path']))})
    self.path = ${render_utils.make_path(msg)}
end

    % endif
  % endfor
% endif
return ${root['package']}
