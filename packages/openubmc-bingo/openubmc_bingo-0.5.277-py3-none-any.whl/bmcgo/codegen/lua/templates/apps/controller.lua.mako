${make_header('lua')}
<%
methods = ['get', 'post', 'patch', 'delete']
package_name = root['package'] != 'Root'
controllers = [msg for msg in root['data'] if "url" in msg["options"]]
messages = [msg for msg in root['data'] if "url" not in msg["options"] and msg['type'] != 'Enum']
enums = [msg for msg in root['data'] if msg['type'] == 'Enum']
%>
local Controller = require 'http.controller'
% if package_name:
local validate = require 'mc.validate'
local error = require 'mc.error'
local http = require 'http'
local safe_call = error.safe_call
local reply_bad_request = http.reply_bad_request
local utils = require 'mc.utils'
% endif
% if project_name == 'redfish':
local redfish_utils = require 'redfish_utils'
% endif
% if len(enums) > 0:
local create_enum_type = require 'mc.enum'
% endif
<%namespace name="message" file="utils/message.mako"/>
<%namespace name="validate" file="utils/validate.mako"/>
<%namespace name="enum" file="utils/enum.mako"/>
<%namespace name="imports" file="utils/imports.mako"/>
${imports.render(root)}
local ${root['package']} = {}

<%def name="get_auth(method, controller, req)">
  local reply = self:auth(ctx)
  if not reply:isOk() then
    return reply
  end
</%def>

<%def name="try_render_patch_methods(method, controller, body)">
  % if body and method == 'patch':
${message.group(utils_py.make_get_message(body['type']),controller)}
  % endif
</%def>
<%def name="http_patch(method, controller, req)">
  local errs = {}
  local body = ${render_utils.get_body(req)['type']}.from_obj(validate.Json(ctx.req.body)):validate('', errs)
  ${render_utils.get_body(req)['type']}:remove_error_props(errs, body)
  local result = {}
  if next(errs) then
    result = http.reply(http.HTTP_BAD_REQUEST, {error = errs})
  else
    result = http.reply_ok()
  end
${message.join_group(utils_py.make_get_message(render_utils.get_body(req)['type']))}
  local req = {user = ctx.user, params = ctx.req.params, path = ctx.req.path, body = body, result = result}
</%def>
<%def name="http_post(method, controller, req)">
  % if render_utils.get_body(req):
  local err, body = safe_call(function()
    return ${render_utils.get_body(req)['type']}.from_obj(validate.Json(ctx.req.body)):validate()
    end)
  if err then
    return reply_bad_request(err.name, err.message)
  end
    % if render_utils.get_header(req) and project_name == 'web_backend':
  local req = {user = ctx.user, params = ctx.req.params, path = ctx.req.path, body = body, header = header}
    % else:
  local req = {user = ctx.user, params = ctx.req.params, path = ctx.req.path, body = body}
    % endif
  % endif
  % if render_utils.get_formdata_body(req):
  ${http_formdata_post(method, controller, req)}
  % endif
</%def>
<%def name="http_formdata_post(method, controller, req)">
  local req_body
  local form_data = require 'http.form_data'
  local form_data_flag, boundary = form_data.is_form_data_req(ctx.req.header)
  if form_data_flag then
      req_body = form_data.decode_form_data(ctx.req.body, boundary)
  else
      req_body = ctx.req.body
  end
  local req = {user = ctx.user, params = ctx.req.params, path = ctx.req.path, body = req_body}
</%def>
<%def name="http_delete(method, controller, req)">
  % if render_utils.get_body(req):
  local err, body = safe_call(function()
    return ${render_utils.get_body(req)['type']}.from_obj(validate.Json(ctx.req.body)):validate()
    end)
  if err then
    return reply_bad_request(err.name, err.message)
  end
  local req = {user = ctx.user, params = ctx.req.params, path = ctx.req.path, body = body}
  % else:
  local req = {user = ctx.user, params = ctx.req.params, path = ctx.req.path}
  % endif
</%def>
<%def name="render_http_method(method, controller, req)">
${try_render_patch_methods(method, controller, render_utils.get_body(req))}
function C${controller['name']}:${method}(ctx)
    % if 'auth' in controller["options"]:
${get_auth(method, controller, req)}
    % endif
    % if render_utils.get_header(req) and project_name == 'redfish':
  local err_header_check = safe_call(function()
    return ${render_utils.get_header(req)['type']}.from_obj(ctx.req.header):validate()
    end)
  if err_header_check and not validate.IsUnknowPropertyErr(err_header_check) then
    return reply_bad_request(err_header_check.name, err_header_check.message)
  end
    % endif
    % if render_utils.get_header(req) and project_name == 'web_backend':
  local header_errs = {}
  local webrest_utils = require 'webrest_utils'
  local header = ${render_utils.get_header(req)['type']}.from_obj(ctx.req.header)
  webrest_utils.remove_unknow_property(header, header.proto_property)
  header:validate('', header_errs)
  if next(header_errs) then
      return webrest_utils.parse_req_result(http.reply(http.HTTP_BAD_REQUEST, {error = header_errs}))
  end
    % endif
    % if method != 'get' and project_name == 'web_backend':
      % if 'system_lockdown' not in req["options"] or req["options"]['system_lockdown'] != 'allow':
  local webrest_utils = require 'webrest_utils'
  if ctx.unit_test ~= true and webrest_utils.get_system_lockdown_state() == true then
    return reply_bad_request('SystemLockdownForbid')
  end
      % endif
    % endif
    % if method == 'post':
${http_post(method, controller, req)}
    % endif
    % if method == 'delete':
${http_delete(method, controller, req)}
    % endif
    % if render_utils.get_body(req) and method == 'patch':
${http_patch(method, controller, req)}
    % endif
    % if method == "get" and render_utils.get_header(req) and not 'auth' in controller["options"]:
  local req = {user = {UserName = '<su>'}, params = ctx.req.params, path = ctx.req.path, header = header}
    % elif method == "get" and render_utils.get_header(req):
  local req = {user = ctx.user, params = ctx.req.params, path = ctx.req.path, header = header}
    % elif method == "get" and not 'auth' in controller["options"]:
  local req = {user = {UserName = '<su>'}, params = ctx.req.params, path = ctx.req.path}
    % elif method == "get":
  local req = {user = ctx.user, params = ctx.req.params, path = ctx.req.path}
    % endif
    % if project_name == 'redfish' or method == "get" and 'query' in controller["options"]:
  local query = require 'http.query'
  req.query = query.parse_query(ctx.req.query)
    % endif
    % if render_utils.get_response(req):
  local rsp_body = ${render_utils.get_response(req)['type']}.new()
    % else:
  local rsp_body = {}
    % endif
  local rsp_header = {}
  local rsp = {body = rsp_body, header = rsp_header}
  % if method == "patch" and project_name == 'redfish':
  local get_req = {path = ctx.req.path}
  local get_rsp = {header = {}}
  local reply = self:process_get(get_req, get_rsp)
  if reply:isOk() == false then
      return reply
  end

  if ctx.req.header['if-match'] == nil or ctx.req.header['if-match'] ~= reply:headers()['ETag'] then
      return http.reply(http.HTTP_PRECONDITION_FAILED, '', reply:headers())
  end

  % endif
  % if method == "get" and project_name == 'redfish':
  local reply = self:process_get(req, rsp)
  if redfish_utils.is_need_reply_modified(ctx.req.header or {}, rsp.header) == true then
      return http.reply(http.HTTP_NOT_MODIFIED, '', reply:headers())
  end

  return reply
  % else:
  return self:process_${method}(req, rsp)
  % endif
end

% if project_name == 'web_backend':
function C${controller['name']}:on_${method}(req, rsp)
    local err
  % if method == 'post':
    local task_info
    % if render_utils.get_lua_codegen_version() <= 3:
      err, rsp.body, _, task_info = self.route_mapper:match(req.path, '${method}', {body = req.body, query = req.query, user = req.user})
    % else:
      err, rsp.body, _, task_info = self.worker_ctrl:process(req.path, '${method}', {body = req.body, query = req.query, user = req.user})
    % endif
  % else:
    % if render_utils.get_lua_codegen_version() <= 3:
      err, rsp.body = self.route_mapper:match(req.path, '${method}', {body = req.body, query = req.query, user = req.user})
    % else:
      err, rsp.body = self.worker_ctrl:process(req.path, '${method}', {body = req.body, query = req.query, user = req.user})
    % endif
  % endif
    if err and #err ~= 0 then
        local webrest_utils = require 'webrest_utils'
        return webrest_utils.parse_route_mapper_error(err)
    end
  % if method == 'patch':
    % if render_utils.get_lua_codegen_version() <= 3:
      _, rsp.body = self.route_mapper:match(req.path, 'get', {body = req.body, query = req.query, user = req.user})
    % else:
      _, rsp.body = self.worker_ctrl:process(req.path, 'get', {body = req.body, query = req.query, user = req.user})
    % endif
  % endif
  % if method == 'post':
    if task_info then
        rsp.task = true
        local task_mgnt = require 'task_mgnt'
        task_mgnt.get_instance():create_new_task(self.app.bus, task_info.Path, task_info.TaskId)
    end
  % endif
end
% endif
% if project_name == 'redfish':
function C${controller['name']}:on_${method}(req, rsp)
  % if method == 'get':
    local err
    err, rsp.body = redfish_utils.get_rsp_body(self, req)
  % else:
    local err, extra_info
    % if render_utils.get_lua_codegen_version() <= 3:
      err, rsp.body, extra_info = self.route_mapper:match(req.path, '${method}', {body = req.body, query = req.query, user = req.user})
    % else:
      err, rsp.body, extra_info = self.worker_ctrl:process(req.path, '${method}', {body = req.body, query = req.query, user = req.user})
    % endif
  % endif
  % if method == 'post' or method == 'delete' or method == 'get':
    if err and #err ~= 0 then
        return redfish_utils.parse_route_mapper_error(err)
    end
  % endif
  % if method == 'patch':
    if err and #err ~= 0 then
        local result = redfish_utils.parse_route_mapper_error(err, '${method}', req.body, extra_info and extra_info.SuccessfulExecute)
        if result:isOk() then
            local extend_info = result:body()['error']['@Message.ExtendedInfo']
            _, rsp.body = redfish_utils.get_rsp_body(self, req)
            rsp.body['@Message.ExtendedInfo'] = extend_info
            return
        end
        return result
    end
    _, rsp.body = redfish_utils.get_rsp_body(self, req)
  % endif
  % if method == 'post' or method == 'delete':
    if extra_info and extra_info.TaskInfo then
        rsp.task = true
        local task_mgnt = require 'redfish.protocol.task_mgnt'
        task_mgnt.get_instance():create_new_task(self.app.bus, extra_info.TaskInfo.Path, extra_info.TaskInfo.TaskId)
    end
  % endif
end
% endif
</%def>

<%def name="render_controller(msg)">
local C${msg['name']} = Controller.new('${msg["options"]['url']}')
%if 'require_auth' in msg["options"]:
local auth = '${msg["options"]['require_auth']}'
% endif
    % for p in msg['properties']:
C${msg['name']}:add_child(${p['type']})
    %endfor

    % for method, method_prop in render_utils.get_controller_methods(msg).items():
${render_http_method(method, msg, method_prop)}
    % endfor

${root['package']}.${msg['name']} = C${msg['name']}
</%def>
% for msg in enums:
${enum.render(msg, 'create_enum_type')}
${root['package']}.${msg['name']} = E${msg['name']}
% endfor

% for msg in messages:
${message.render(msg)}
${root['package']}.${msg['name']} = T${msg['name']}
% endfor

% for msg in controllers:
${render_controller(msg)}
% endfor

return ${root['package']}