${make_header('lua')}
<%
messages = [msg for msg in root['data'] if msg['type'] != 'Enum']
enums = [msg for msg in root['data'] if msg['type'] == 'Enum']
%>
local validate = require 'mc.validate'
local utils = require 'mc.utils'
% if 'intf' in root:
local mdb = require 'mc.mdb'
% endif
% if len(enums) > 0:
local create_enum_type = require 'mc.enum'
% endif
<%namespace name="message" file="utils/message.mako"/>
<%namespace name="imports" file="utils/imports.mako"/>
<%namespace name="enum" file="utils/enum.mako"/>
<%namespace name="mdb_intf" file= "utils/mdb_intf.lua.mako"/>
${imports.render(root)}

local ${root['package']} = {}

% for msg in enums:
${enum.render(msg, 'create_enum_type')}
${root['package']}.${msg['name']} = E${msg['name']}

% endfor

% for msg in messages:
${message.render(msg, root.get('intf', {}).get('name', ''))}

${root['package']}.${msg['name']} = T${msg['name']}
% endfor

% if 'intf' in root:
${root['package']}.interface = ${mdb_intf.render(root['intf'])}

% endif
return ${root['package']}