

<%def name="render(class_name, class_data, class_require)">
  % if 'path' in class_data:
    path = '${render_utils.get_path(class_name, class_require)}',
    % if 'interfaces' in class_data:
      interface_data = {
        % for intf in class_data['interfaces']:
          {name = '${intf}'},
        % endfor
      }
    %endif
  %endif
</%def>