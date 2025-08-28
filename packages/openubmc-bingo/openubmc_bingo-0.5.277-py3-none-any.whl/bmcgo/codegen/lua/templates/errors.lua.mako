${make_header('lua')}
local log = require 'mc.logging'
local error = require 'mc.error'
local new_error = error.new_error
local print_log = error.print_log
local print_trace = error.print_trace
local regist_err_eng = error.register_err

local M = {}

% for name, err in root['messages'].items() :
local ${render_utils.get_error_name(name)} = {
    name = "${name}",
    format = ${utils_py.format_value(render_utils.format(err['message']), '')},
    % if 'backtrace_level' in err :
    backtrace_level = ${err['backtrace_level']},
    % endif
    % if 'severity' in err :
    severity = '${err['severity']}',
    % endif
}
M.${render_utils.get_error_name(name)} = ${render_utils.get_error_name(name)}.name
---@return Error
function M.${render_utils.get_function_name(name)}(${render_utils.params(err['message'])})
    local err_data = new_error(${render_utils.get_error_name(name)}.name, ${render_utils.get_error_name(name)}.format${render_utils.error_params(err)})
    regist_err_eng(${render_utils.get_error_name(name)}, ${render_utils.get_http_response(root, err)}, ${render_utils.get_redfish_response(root, err)}, ${render_utils.get_ipmi_response_json(err)})
    print_log(${render_utils.get_severity_err(err)}, ${render_utils.get_error_name(name)}.format${render_utils.error_params(err)})
    % if 'backtrace_level' in err and err['backtrace_level'] > 0 :
    print_trace(${render_utils.get_backtrace_level(root, err)}, err_data) -- the first parameter means backtrace level
    % endif
    return err_data
end

% endfor

return M
