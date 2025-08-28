<%def name="render_import(pkg, path)">local ${pkg} = require "${path.replace('.proto', "").replace("/", ".")}"</%def>

<%def name="render(root)">
% if 'dependency' in root:
    % for (pkg, data) in root['dependency'].items():
        % if "require_path" in data:
local ${pkg} = require "${data["require_path"]}"
        % else:
${render_import(pkg, f"{project_name}.{data['filename']}")}
        % endif
    % endfor
% endif
</%def>
