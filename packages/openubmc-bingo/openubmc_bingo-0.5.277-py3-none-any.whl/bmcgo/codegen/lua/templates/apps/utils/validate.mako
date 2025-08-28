
<%def name="render_base(msg_type, prefix, name_prefix)">
  % for v in render_utils.get_validates(utils_py.make_get_message(msg_type)):
    % if len(v[1]) > 0:
    % if not render_utils.is_required(v[0]):
  if ${render_utils.proper_name(v[0].get('original_name', v[0]['name']), prefix)} ~= nil then
    % for vv in v[1]:
    validate.${vv[0]}(${render_utils.validate_name(v[0].get('original_name', v[0]['name']), name_prefix)}, ${render_utils.proper_name(v[0].get('original_name', v[0]['name']), prefix)}, ${", ".join(vv[1])}${render_utils.readonly(vv[0],v[0].get('original_name', v[0]['name']),v[0]['type'],v[0]['options'])}, errs, need_convert)
    % endfor
  end
    % else:
    % for vv in v[1]:
  validate.${vv[0]}(${render_utils.validate_name(v[0].get('original_name', v[0]['name']), name_prefix)}, ${render_utils.proper_name(v[0].get('original_name', v[0]['name']), prefix)}, ${", ".join(vv[1])}${render_utils.readonly(vv[0],v[0].get('original_name', v[0]['name']),v[0]['type'],v[0]['options'])}, errs, need_convert)
    % endfor
    %endif
    %endif
  %endfor
</%def>

<%def name="render(msg_type, prefix, name_prefix)">
  % for v in render_utils.get_requires(utils_py.make_get_message(msg_type)):
    % for vv in v[1]:
  validate.${vv[0]}(${render_utils.validate_name(v[0].get('original_name', v[0]['name']), name_prefix)}, ${render_utils.proper_name(v[0].get('original_name', v[0]['name']), prefix)}, ${", ".join(vv[1])}${render_utils.readonly(vv[0],v[0].get('original_name', v[0]['name']),v[0]['type'],v[0]['options'])}, errs, need_convert)
    % endfor
  % endfor
  ${render_base(msg_type,  prefix, name_prefix)}
</%def>

<%def name="render_struct(msg_type, prefix, name_prefix)">
  <% msg = utils_py.make_get_message(msg_type)%>
  <% print(msg) %>
  % for name, t in render_utils.get_struct_requires(msg).items():
    % if t['repeated'] :
  for _,v in pairs(self.${name}) do
    ${t['type']}.new(${render_utils.params1('v', utils_py.make_get_message(t['type']))}):validate(prefix, errs, need_convert)
  end
    % else:
  ${t['type']}.new(${render_utils.params1('self.' + name, utils_py.make_get_message(t['type']))}):validate(prefix, errs, need_convert)
  % endif
  % endfor

  % for v in render_utils.get_no_struct_requires(utils_py.make_get_message(msg_type)):
    % for vv in v[1]:
  validate.${vv[0]}(${render_utils.validate_name(v[0].get('original_name', v[0]['name']), name_prefix)}, ${render_utils.proper_name(v[0].get('original_name', v[0]['name']), prefix)}, ${", ".join(vv[1])}${render_utils.readonly(vv[0],v[0].get('original_name', v[0]['name']),v[0]['type'],v[0]['options'])}, errs, need_convert)
    % endfor
  % endfor
  ${render_base(msg_type,  prefix, name_prefix)}
</%def>

<%def name="render_dict_item(msg_type, index, prefix, name_prefix)">
  <% v = render_utils.get_requires(utils_py.make_get_message(msg_type))[index] %>
    % for vv in v[1]:
  validate.${vv[0]}(${render_utils.validate_name(v[0].get('original_name', v[0]['name']), name_prefix)}, ${'k' if index == 0 else 'v'}, ${", ".join(vv[1])}${render_utils.readonly(vv[0],v[0].get('original_name', v[0]['name']),v[0]['type'],v[0]['options'])}, errs, need_convert)
    % endfor
  ${render_base(msg_type,  prefix, name_prefix)}
</%def>

<%def name="render_dict_struct_item(msg_type, index, prefix, name_prefix)">
  <% value = 'k' if index == 0 else 'v' %>
  <% v = render_utils.get_requires(utils_py.make_get_message(msg_type))[index] %>
  <% name = v[0].get('original_name', v[0]['name']) %>
  <% t = render_utils.get_struct_require(v[0]) %>
  % if t['repeated'] :
  for _,q in pairs(${value}) do
    ${t['type']}.new(${render_utils.params1('q', utils_py.make_get_message(t['type']))}):validate(prefix, errs, need_convert)
  end
  % else:
  ${t['type']}.new(${render_utils.params1(value, utils_py.make_get_message(t['type']))}):validate(prefix, errs, need_convert)
  % endif
  ${render_base(msg_type,  prefix, name_prefix)}
</%def>

<%def name="render_dict(msg, prefix, name_prefix)">
  for k, v in pairs(self) do
  % for i, prop in enumerate(msg['properties']):
    %if msg['options'] and prop.get('is_struct', False):
  ${render_dict_struct_item(msg['name'], i, prefix, name_prefix)}
    %else:
  ${render_dict_item(msg['name'], i, prefix, name_prefix)}
    %endif
  %endfor
  end
</%def>