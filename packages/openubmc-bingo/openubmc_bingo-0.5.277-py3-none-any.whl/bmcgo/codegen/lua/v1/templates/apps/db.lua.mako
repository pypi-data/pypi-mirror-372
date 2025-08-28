${make_header('lua')}
local class = require 'mc.class'
local db_base = require 'database.db_base'
local Col = require 'database.column'
<%namespace name="imports" file="../../../templates/apps/utils/imports.mako"/>
${imports.render(root)}
<%
ClassName = root['package'] + 'Database'
%>

% for msg in root['data']:
  % if render_utils.table_name(msg):
---@class ${msg['name']}Table: Table
% for prop in msg['properties']:
---@field ${prop['name']} FieldBase
% endfor
  % endif

% endfor

---@class ${ClassName}
---@field db DataBase
% for msg in root['data']:
  % if render_utils.table_name(msg):
---@field ${msg['name']} ${msg['name']}Table
  % endif
% endfor
local ${ClassName} = class(db_base)

function ${ClassName}:ctor()
% for msg in root['data']:
  % if render_utils.table_name(msg):
  self.${msg['name']} = self.db:Table('${render_utils.table_name(msg)}', {
    % for prop in msg['properties']:
    ${prop['name']} = Col.${render_utils.column_type(prop)}:cid(${prop['id']})${render_utils.primary_key(prop)}${render_utils.persistence_key(prop)}${render_utils.unique(prop)}${render_utils.allow_null(prop)}${render_utils.max_len(prop)}${render_utils.default(msg['name'], prop)}${render_utils.critical(prop)},
    % endfor
    % if render_utils.all_persistence(msg) != 'nil':
    }, "${render_utils.all_persistence(msg)}"):create_if_not_exist(self.datas and self.datas['${render_utils.table_name(msg)}'])
    % else:
    }):create_if_not_exist(self.datas and self.datas['${render_utils.table_name(msg)}'])
    % endif
      % if render_utils.table_max_rows(msg) and render_utils.get_lua_codegen_version() >= 11:
    self.${msg['name']}.table_max_rows = ${msg['options']['table_max_rows']}
      %endif
  % endif
% endfor

  self.tables = self.db.tables
end

% for msg in root['data']:
  % if render_utils.table_name(msg):
    % if render_utils.table_max_rows(msg) and render_utils.get_lua_codegen_version() >= 11:
  
function ${ClassName}:Register${msg['name']}TableMaxRowsCallback(cb)
  self.${msg['name']}.table_max_rows_cb = cb
end
    % endif
  % endif
% endfor

return ${ClassName}.new
