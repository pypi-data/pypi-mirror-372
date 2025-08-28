${make_header('proto')}
syntax = "proto3";
import "types.proto";
import "apps/redfish/types/common.proto";
import "apps/redfish/types/resource.proto";
%if utils_py.oem_is_exist(render_utils.get_file_name()):
import "apps/redfish/resource/oem/hw/${render_utils.get_file_name()}.proto";${load_import(f"apps/redfish/resource/oem/hw/{render_utils.get_file_name()}.proto",render_utils.get_file_name())}
%endif
package ${render_utils.get_file_name()};
<%def name="unpack_enum(key,properties)">
%for idx, val in enumerate(properties):
    ${key}_${render_utils.replace_tag(val)} = ${idx};
%endfor
</%def>
<%def name="unpack_propties(k,properties)">
%for idx, val in enumerate([(k, v) for k, v in properties.items()]):
    %if val[0] == 'PowerState':
    Resource.PowerState PowerState = ${idx+1}${render_utils.attr_option_field(val[1])};
    %elif val[0] == 'Oem' and utils_py.oem_is_exist(render_utils.get_file_name()) and utils_py.is_oem_message(render_utils.get_file_name(),k):
    ${utils_py.get_oem_message(render_utils.get_file_name(),k)['package']}.${k} oem = ${idx+1}${render_utils.attr_option_field(val[1])};
    %elif 'type' in val[1] and 'items' in val[1]:
        %if 'anyOf' in val[1]['items']:
    ${render_utils.get_class_name(val[1]['items']['anyOf'][0]['$ref'])} ${render_utils.replace_tag(val[0])} = ${idx+1}${render_utils.attr_option_field(val[1])};
        %elif 'type' in val[1]['items'] :
    repeated ${render_utils.get_type(val[0],val[1]['items']['type'])} ${render_utils.replace_tag(val[0])} = ${idx+1}${render_utils.attr_option_field(val[1])};
        %else:
    ${render_utils.get_class_name(val[1]['items']['$ref'])} ${render_utils.replace_tag(val[0])} = ${idx+1}${render_utils.attr_option_field(val[1])};
        %endif
    %elif '$ref' in val[1]:
    ${render_utils.get_class_name(val[1]['$ref'])} ${render_utils.replace_tag(val[0])} = ${idx+1}${render_utils.attr_option_field(val[1])};
    %elif 'anyOf' in val[1]:
    ${render_utils.get_class_name(val[1]['anyOf'][0]['$ref'])} ${render_utils.replace_tag(val[0])} = ${idx+1}${render_utils.attr_option_field(val[1])};
    %elif 'type' in val[1]:
    ${render_utils.get_type(val[0],val[1]['type'])} ${render_utils.replace_tag(val[0])} = ${idx+1}${render_utils.attr_option_field(val[1])};
    %else:
    ${val[0]} ${render_utils.replace_tag(val[0])} = ${idx+1}${render_utils.attr_option_field(val[1])};
    %endif
%endfor
</%def>
%for k,v in root['definitions'].items():
    %if 'enum' in v and k != 'PowerState':
enum ${k} {${unpack_enum(k,v['enum'])}}
    %elif 'properties' in v:
message ${k} {${unpack_propties(k, v['properties'])}}
    %endif

%endfor
