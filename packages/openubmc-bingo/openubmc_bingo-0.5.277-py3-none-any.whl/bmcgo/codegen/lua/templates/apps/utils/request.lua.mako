<%def name="assign_property_by_kepler(msg, before_name)">
    % for pt in msg.properties:
        %if pt.complex_type(render_utils.msg_mgr):
            %if before_name == "":
    ${assign_property_by_kepler(render_utils.get(pt.attr_type), "rsp")}
            %else:
    ${assign_property_by_kepler(render_utils.get(pt.attr_type), f"{before_name}['{pt.out_attr_name}']")}
            %endif
        %else:
            %if pt.attr_to_view.valid():
                %if pt.attr_to_view.use_self:
    ${before_name}['${pt.out_attr_name}'] = ${pt.attr_to_view.cvt_fun}(${render_utils.inner_var(message_name, pt)}.${pt.mapping.inner_attr_name}:value(), ${render_utils.inner_var(message_name, pt)})
                %else:
    ${before_name}['${pt.out_attr_name}'] = ${pt.attr_to_view.cvt_fun}(${render_utils.inner_var(message_name, pt)}.${pt.mapping.inner_attr_name}:value())
                %endif
            %else:
    ${before_name}['${pt.out_attr_name}'] = ${render_utils.inner_var(message_name, pt)}.${pt.mapping.inner_attr_name}:value()
            %endif
        %endif
    % endfor
</%def>
<%def name="assign_property_by_redfish(msg, before_name)">
    % for pt in msg.properties:
        %if pt.complex_type(render_utils.msg_mgr):
            %if before_name == "":
    ${assign_property_by_redfish(render_utils.get(pt.attr_type), "req.body")}
            %else:
    ${assign_property_by_redfish(render_utils.get(pt.attr_type), f"{before_name}['{pt.out_attr_name}']")}
            %endif
        %else:
            %if pt.attr_to_view.valid():
                %if pt.attr_to_view.use_self:
    ${render_utils.inner_var(message_name, pt)}.${pt.mapping.inner_attr_name} = ${pt.attr_to_view.cvt_fun}(${before_name}['${pt.out_attr_name}'], ${before_name})
                %else:
    ${render_utils.inner_var(message_name, pt)}.${pt.mapping.inner_attr_name} = ${pt.attr_to_view.cvt_fun}(${before_name}['${pt.out_attr_name}'])
                %endif
            %else:
    ${render_utils.inner_var(message_name, pt)}.${pt.mapping.inner_attr_name} = ${before_name}['${pt.out_attr_name}']
            %endif
        %endif
    % endfor
</%def>
<%def name="get(message_name)">
function CRoute:fill_get_response(req, rsp)
    % for item in render_utils.related_objects(message_name).url_dict.items():
    local ${render_utils.related_message(item[1].url_feature).class_var_name()} = self.app.bus:call_get_all(${item[0]})
    % endfor
${assign_property_by_kepler(render_utils.get(message_name), "")}
end
</%def>
<%def name="patch(message_name)">
function CRoute:new_kepler_objects(req)
    % for item in render_utils.related_objects(message_name).url_dict.items():
    local ${render_utils.related_message(item[1].url_feature).class_var_name()} = ${render_utils.related_message(item[1].url_feature).class_type()}.new()
    % endfor
    ${assign_property_by_redfish(render_utils.get(message_name), "")}
    return ${", ".join([render_utils.related_message(item[1].url_feature).class_var_name() for item in render_utils.related_objects(message_name).url_dict.items()])}
end
</%def>