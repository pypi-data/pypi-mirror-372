${make_header('lua')}

local factory = require '${project_name}.factory'
local class = require 'mc.class'

local ${class_name.lower()} = class()

% for interface in model[class_name].get('interfaces', []):
    % for method in model[class_name]['interfaces'][interface].get('methods', []):
<% method_dict = model[class_name]['interfaces'][interface]['methods'][method] %>
<% intf_name = interface.split('.')[-1] %>
    % if intf_name == 'Default':
    <% pre_intf_name = interface.split('.')[-2] %>
function ${class_name.lower()}:${class_name}${pre_intf_name}${intf_name}${method}(obj, ctx${''.join([', ' + key for key in method_dict.get('req', dict()).keys()])})
    % else:
    <% unique_intf_name = render_utils.get_unique_intf_name(interface) %>
function ${class_name.lower()}:${class_name}${unique_intf_name}${method}(obj, ctx${''.join([', ' + key for key in method_dict.get('req', dict()).keys()])})
    % endif

    return 0
end

    % endfor
%endfor
function ${class_name.lower()}:on_add_object(class_name, object, position)

    return
end

function ${class_name.lower()}:on_del_object(class_name, object, position)

    return
end

factory.register_to_factory('${class_name}', ${class_name.lower()})