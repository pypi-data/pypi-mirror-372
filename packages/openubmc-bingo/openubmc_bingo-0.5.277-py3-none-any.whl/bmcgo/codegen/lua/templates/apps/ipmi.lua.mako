--[[${make_header('lua')}]]--
<%namespace name="imports" file="utils/imports.mako"/>
<%
ClassName = root['package']
%>
% if render_utils.has_generate_client():
local bs = require 'mc.bitstring'
local enums = require 'ipmi.enums'
local ipmi = require 'ipmi'
% endif
% if render_utils.has_generate_service():
local types = require 'ipmi.types'
local privilege = require 'mc.privilege'
% endif
local msg = require "${project_name}.${root['filename'].replace('.proto', "").replace("/", ".")}_message"

% if render_utils.has_generate_client():
local CT = enums.ChannelType
% endif

local ${ClassName} = {}

% for ipmi in root['data']:
  % if "nested_type" in ipmi and len(ipmi["nested_type"]) > 0:
  % if render_utils.is_generate_service(ipmi):

${ClassName}.${ipmi['name']} = {
    name = '${ipmi['name']}',
% if version >= 5:
    prio = types.Priority.${render_utils.get_priority(ipmi)},
% else:
    prio = types.Prio.${render_utils.get_priority(ipmi)},
% endif
    netfn = ${render_utils.format_hex(render_utils.get_netfn(ipmi))},
    cmd = ${render_utils.format_hex(ipmi['options']['cmd'])},
% if version >= 5:
    role = types.Role.${ipmi['options']['role']},
% else:
    role = types.Privilege.${ipmi['options']['role']},
% endif
    privilege = ${render_utils.get_privilege(ipmi)},
    sensitive = ${'true' if ipmi['options']['sensitive'] else 'false'},
    restricted_channels = ${render_utils.get_restricted_channel(ipmi)},
    filters = ${utils_py.format_value(render_utils.get_option(ipmi, 'filters'), '')},
    decode = ${utils_py.format_value(render_utils.get_option(ipmi, 'decode'), '')},
    encode = ${utils_py.format_value(render_utils.get_option(ipmi, 'encode'), '')},
    req = msg.${ipmi['name']}Req,
    rsp = msg.${ipmi['name']}Rsp,
% if version >= 3:
    manufacturer = ${utils_py.format_value(render_utils.get_manufacturer(ipmi), '')},
% endif
    sysLockedPolicy = '${render_utils.get_sys_locked_policy(ipmi)}'
}
  % else:

% if render_utils.get_option(ipmi, 'decode') != '':
local ${utils_py.camel_to_snake(ipmi['name'])}_req = nil
% endif
% if render_utils.get_option(ipmi, 'encode') != '':
local ${utils_py.camel_to_snake(ipmi['name'])}_rsp = nil
% endif
  % for p in render_utils.req_properties(ipmi):
---@param ${p['name']} ${utils_py.do_type_to_lua(p['type'], p['repeated'])}
  % endfor
  % for p in render_utils.rsp_properties(ipmi):
---@return ${p['name']} ${utils_py.do_type_to_lua(p['type'], p['repeated'])}
  % endfor
% if render_utils.req_params(ipmi) != '':
function ${ClassName}.${ipmi['name']}(bus, ${render_utils.req_params(ipmi)})
% else:
function ${ClassName}.${ipmi['name']}(bus)
% endif
    % if render_utils.get_option(ipmi, 'decode') != '':
    ${utils_py.camel_to_snake(ipmi['name'])}_req = ${utils_py.camel_to_snake(ipmi['name'])}_req or bs.new('${render_utils.get_option(ipmi, 'decode')}')
    % endif
    % if render_utils.get_option(ipmi, 'encode') != '':
    ${utils_py.camel_to_snake(ipmi['name'])}_rsp = ${utils_py.camel_to_snake(ipmi['name'])}_rsp or bs.new('${render_utils.get_option(ipmi, 'encode')}')
    % endif
    % if render_utils.get_option(ipmi, 'decode') != '':
    local data = ${utils_py.camel_to_snake(ipmi['name'])}_req:pack(${render_utils.req_json(ipmi)})
    % else:
    local data = ''
    % endif
    local cc, payload = ipmi.request(bus, CT.${render_utils.get_channel(ipmi)}:value(), {DestNetFn = ${render_utils.format_hex(ipmi['options']['net_fn'])}, Cmd = ${render_utils.format_hex(ipmi['options']['cmd'])}, Payload = data})

    % if render_utils.get_option(ipmi, 'encode') != '':
    msg.${ipmi['name']}Rsp.new(${utils_py.camel_to_snake(ipmi['name'])}_rsp:unpack(payload)):validate()
    return cc, ${utils_py.camel_to_snake(ipmi['name'])}_rsp:unpack(payload)
    % else:
    return cc, payload
    % endif
end
  % endif
  % endif
% endfor

return ${ClassName}