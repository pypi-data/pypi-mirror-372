<%namespace name="validate" file="validate.mako"/>
<%def name="group(msg,controller)">
%for k,msg in render_utils.get_group_fields(msg).items():
function C${controller['name']}:set_group${k}(user, ${render_utils.get_group_names_for_set(msg)})
end

%endfor
</%def>
<%def name="join_group(msg)">
%for k,msg in render_utils.get_group_fields(msg).items():
  result:join(self:set_group${k}(user, ${render_utils.get_group_names_for_join(msg)}))
%endfor
</%def>
<%def name="render(msg, intf_name='')">
% if 'properties' in msg:
---@class ${msg['package']}.${msg['name']}
  % for p in msg['properties']:
---@field ${p.get('original_name', p['name'])} ${utils_py.do_type_to_lua(p['type'], 'repeated' in p and p['repeated'])}
  % endfor
local T${msg['name']} = {}
T${msg['name']}.__index = T${msg['name']}
T${msg['name']}.group = {${render_utils.get_groups(msg)}}

local function T${msg['name']}_from_obj(obj)
    % for m in render_utils.get_enums(msg):
      % if 'repeated' in m and m['repeated']:
  obj.${m['name']} = utils.from_obj(${m['type']}, obj.${m['name']}, true)
      % else:
  obj.${m['name']} = obj.${m['name']} and ${m['type']}.new(obj.${m['name']})
      % endif
    %endfor
    % for m in render_utils.get_sub_type(msg):
      % if  'repeated' in m and m['repeated']:
  obj.${m['name']} = utils.from_obj(${m['type']}, obj.${m['name']}, true)
      % else:
  obj.${m['name']} = utils.from_obj(${m['type']}, obj.${m['name']})
      % endif
    %endfor
    % for e in render_utils.get_enums(msg):
    %endfor
    % for m in render_utils.get_sub_type(msg):
    %endfor
    % for a, b in render_utils.get_rename_fields(msg):
    utils.rename(obj, "${b}", "${a}")
    %endfor
  return setmetatable(obj, T${msg['name']})
end

  %if msg['type'] == "Dictionary":
function T${msg['name']}.new(dict)
  return T${msg['name']}_from_obj(dict)
end

---@param obj ${msg['package']}.${msg['name']}
function T${msg['name']}:init_from_obj(obj)
  self = obj
end

function T${msg['name']}:remove_error_props(errs, obj)
  utils.remove_obj_error_property(obj, errs, T${msg['name']}.group)
end

T${msg['name']}.from_obj = T${msg['name']}_from_obj

T${msg['name']}.proto_property = {}

T${msg['name']}.default = {}

T${msg['name']}.struct = {}

function T${msg['name']}:validate(prefix, errs, need_convert)
  prefix = prefix or ''
  ${validate.render_dict(msg, 'self.', 'prefix')}
  T${msg['name']}:remove_error_props(errs, self)
  return self
end

function T${msg['name']}:unpack(_)
  return self
end
  % else:
function T${msg['name']}.new(${render_utils.params(msg)})
  return T${msg['name']}_from_obj({
    ${utils_py.construct(msg)}
  })
end
---@param obj ${msg['package']}.${msg['name']}
function T${msg['name']}:init_from_obj(obj)
  ${render_utils.obj_construct(msg)}
end

function T${msg['name']}:remove_error_props(errs, obj)
  utils.remove_obj_error_property(obj, errs, T${msg['name']}.group)
end

T${msg['name']}.from_obj = T${msg['name']}_from_obj

T${msg['name']}.proto_property = {
  % for v in render_utils.get_requires(utils_py.make_get_message(msg['name'])):
    % for vv in v[1]:
  '${v[0].get('original_name', v[0]['name'])}',
    % endfor
  % endfor
}

T${msg['name']}.default = {
  % for v in render_utils.get_requires(utils_py.make_get_message(msg['name'])):
    % for vv in v[1]:
      % for vvv in vv[1]:
  ${render_utils.get_default(vv[0], vvv)},
      % endfor
    % endfor
  % endfor
}

% if version >= 16:
${render_utils.get_descriptions(msg, intf_name)}
%endif

T${msg['name']}.struct = {
  % for v in render_utils.get_requires(utils_py.make_get_message(msg['name'])):
    % for vv in v[1]:
      % for vvv in vv[1]:
  {name = '${v[0].get('original_name', v[0]['name'])}', is_array = ${render_utils.is_array(vv[0])}, struct = ${render_utils.get_struct(vvv)}},
      % endfor
    % endfor
  % endfor
}

function T${msg['name']}:validate(prefix, errs, need_convert)
  prefix = prefix or ''
%if 'has_struct' in msg['options'] and msg['options']['has_struct'] :
${validate.render_struct(msg['name'], 'self.', 'prefix')}
%else:
${validate.render(msg['name'], 'self.', 'prefix')}
%endif
  T${msg['name']}:remove_error_props(errs, self)
  validate.CheckUnknowProperty(self, T${msg['name']}.proto_property, errs, need_convert)
  return self
end

    % if len(render_utils.get_enums(msg)) > 0 or len(render_utils.get_sub_type(msg)) > 0:
function T${msg['name']}:unpack(raw)
    % else:
function T${msg['name']}:unpack(_)
    % endif
    % if len(msg['properties']) > 0:
      % for p in render_utils.get_enums(msg):
        % if 'repeated' in p and p['repeated']:
  local ${p.get('original_name', p['name'])} = utils.unpack_enum(raw, utils.from_obj(${p['type']}, self.${p.get('original_name', p['name'])}, true), true)
        % else:
  local ${p.get('original_name', p['name'])} = utils.unpack_enum(raw, self.${p.get('original_name', p['name'])})
        % endif
      % endfor
  return ${render_utils.unpack(msg)}
    % endif
end
  % endif
% endif
</%def>