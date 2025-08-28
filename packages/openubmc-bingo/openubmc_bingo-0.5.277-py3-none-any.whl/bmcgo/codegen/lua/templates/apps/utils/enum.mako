<%def name="render(msg, create_enum_type)">---@class ${msg['package']}.${msg['name']}: Enum
local E${msg['name']} = ${create_enum_type}('${msg['name']}')
% if 'default' in msg:
E${msg['name']}.default = E${msg['name']}.new(${msg['default']})
E${msg['name']}.struct = nil
% endif
% for prop in msg['values']:
E${msg['name']}.${utils_py.enum_value_name(msg['name'], prop['name'])} = E${msg['name']}.new(${("'" + prop['value'] + "'") if type(prop['value']) == str else prop['value']})
% endfor
</%def>
