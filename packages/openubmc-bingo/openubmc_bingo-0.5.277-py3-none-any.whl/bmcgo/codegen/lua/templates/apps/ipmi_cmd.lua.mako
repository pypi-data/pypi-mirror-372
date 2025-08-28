${make_header('lua')}

local factory = require '${project_name}.factory'
local class = require 'mc.class'
local log = require 'mc.logging'
local ipmi_msg = require '${project_name}.ipmi.ipmi'
local ipmi = require 'ipmi'

local ipmi_cmd = class()

% for ipmi_method in ipmi.get('cmds', []):
function ipmi_cmd:${ipmi_method}(req, ctx)

    return
end
% endfor

factory.register_to_factory('ipmi_cmd', ipmi_cmd)