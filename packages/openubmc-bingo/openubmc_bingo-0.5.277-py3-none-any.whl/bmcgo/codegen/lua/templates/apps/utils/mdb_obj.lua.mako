

<%def name="render_sig(class_name, class_data, class_require)">
% if 'path' in class_data:
local ${class_name} = mdb.register_object('${render_utils.get_path(class_name, class_require)}', {
      % if 'interfaces' in class_data:
        % for intf in class_data['interfaces']:
      {name = '${intf}', interface = ${utils_py.get_unique_intf_name(intf)}Types.interface},
        % endfor
      % endif
    })
% endif
</%def>

<%def name="render(class_name, class_data, class_require)">
${render_sig(class_name, class_data, class_require)}

% if 'path' in class_data:
function ${class_name}:ctor(${", ".join(render_utils.get_path_params(render_utils.get_path(class_name, class_require)))})
    self.path = ${render_utils.make_path(render_utils.get_path(class_name, class_require))}
end
% endif
</%def>