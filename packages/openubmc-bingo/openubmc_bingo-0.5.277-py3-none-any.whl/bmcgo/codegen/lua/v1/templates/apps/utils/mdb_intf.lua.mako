<%def name="render(intf)">
{
 '${intf['name']}', {
  % if 'properties' in intf['data'] :
    % for p,p_data in intf['data']['properties'].items():
      ${p} = {'${render_utils.do_type_to_dbus_json(intf['data'], p_data)}', ${render_utils.options_json(p_data)}, ${render_utils.readonly_json(p_data)}, ${render_utils.default_json(p_data)}, false},
    % endfor
  % endif
  }, {
  % if 'methods' in intf['data'] :
    % for method, method_data in intf['data']['methods'].items():
% if version >= 16:
      ${method} = {'a{ss}${render_utils.do_types_to_dbus_json(intf['data'], method_data, 'req')}', '${render_utils.do_types_to_dbus_json(intf['data'], method_data,'rsp')}', T${method}Req, T${method}Rsp${render_utils.get_method_description(intf['name'], method_data)}},
% else:
      ${method} = {'a{ss}${render_utils.do_types_to_dbus_json(intf['data'], method_data, 'req')}', '${render_utils.do_types_to_dbus_json(intf['data'], method_data,'rsp')}', T${method}Req, T${method}Rsp},
%endif
    % endfor
  % endif
  }, {
  % if 'signals' in intf['data'] :
    % for s,s_data in intf['data']['signals'].items():
      ${s} = 'a{ss}${render_utils.do_types_to_dbus_json(intf['data'], intf['data']['signals'], s)}',
    % endfor
  % endif
  }
}
</%def>