--[[${make_header('lua')}]]--
<%
messages = []
for msg in root['data']:
  if 'nested_type' in msg:
    for nest_msg in msg['nested_type']:
      if msg['type'] != 'Enum':
        nest_msg['name'] = msg['name'] + nest_msg['name']
        messages.append(nest_msg)
enums = [msg for msg in root['data'] if msg['type'] == 'Enum']
%>
local validate = require 'mc.validate'
local utils = require 'mc.utils'
% if len(enums) > 0:
local create_enum_type = require 'mc.enum'
% endif
<%namespace name="message" file="utils/message.mako"/>
<%namespace name="imports" file="utils/imports.mako"/>
<%namespace name="enum" file="utils/enum.mako"/>
${imports.render(root)}

local ${root['package']}Msg = {}

% for msg in enums:
${enum.render(msg, 'create_enum_type')}
${root['package']}Msg.${msg['name']} = E${msg['name']}

% endfor

% for msg in messages:
${message.render(msg)}

${root['package']}Msg.${msg['name']} = T${msg['name']}
% endfor

return ${root['package']}Msg