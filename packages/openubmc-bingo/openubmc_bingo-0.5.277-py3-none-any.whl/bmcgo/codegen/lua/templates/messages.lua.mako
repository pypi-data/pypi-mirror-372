${make_header('lua')}
local log = require 'mc.logging'
local error = require 'mc.error'
local create_error = error.create_error
local M = {}
% if 'RegistryPrefix' in root:
M.RegistryPrefix = '${root['RegistryPrefix']}'
% endif
% if 'RegistryVersion' in root:
M.RegistryVersion = '${root['RegistryVersion']}'
% endif
% for name, err in root['Messages'].items():
<% params = render_utils.params(err['Message'])%>
M.${name}Message = {
    Original = ${utils_py.format_value(err, '')},
    Name = "${name}",
    Format = ${utils_py.format_value(render_utils.format(err['Message']), '')},
    BacktraceLevel = ${render_utils.get_backtrace_level(root, err)},
    Severity = ${render_utils.get_severity_err(err)},
    HttpResponse = ${render_utils.get_http_response(root, err)},
    IpmiResponse = ${render_utils.get_ipmi_response(err)},
    % if 'RegistryPrefix' in root:
    RegistryPrefix = '${root['RegistryPrefix']}'
    % endif
}
---@return Error
function M.${name}(${params})
    return create_error(M.${name}Message${render_utils.error_params(err)})
end

% endfor
return M
