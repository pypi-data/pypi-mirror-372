${make_header('lua')}
local Databases = require 'database'
local Col = require 'database.column'
<%namespace name="imports" file="utils/imports.mako"/>
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
---@field select fun(db:DataBase, table: any, ...): SelectStatement
---@field update fun(db:DataBase, table: any, ...): UpdateStatement
---@field insert fun(db:DataBase, table: any, ...): InsertStatement
% for msg in root['data']:
  % if render_utils.table_name(msg):
---@field ${msg['name']} ${msg['name']}Table
  % endif
% endfor
local ${ClassName} = {}
${ClassName}.__index = ${ClassName}

function ${ClassName}.new(path, datas)
  local db = Databases(path)
  local obj = {db = db}

% for msg in root['data']:
  % if render_utils.table_name(msg):
  obj.${msg['name']} = db:Table('${render_utils.table_name(msg)}', {
    % for prop in msg['properties']:
    ${prop['name']} = Col.${render_utils.column_type(prop)}:cid(${prop['id']})${render_utils.primary_key(prop)}${render_utils.persistence_key(prop)}${render_utils.unique(prop)}${render_utils.allow_null(prop)}${render_utils.max_len(prop)}${render_utils.default(msg['name'], prop)}${render_utils.critical(prop)},
    % endfor
    % if render_utils.all_persistence(msg) != 'nil':
    }, "${render_utils.all_persistence(msg)}"):create_if_not_exist(datas and datas['${render_utils.table_name(msg)}'])
    % else:
    }):create_if_not_exist(datas and datas['${render_utils.table_name(msg)}'])
    % endif
      % if render_utils.table_max_rows(msg) and render_utils.get_lua_codegen_version() >= 11:
    obj.${msg['name']}.table_max_rows = ${msg['options']['table_max_rows']}
      %endif
  % endif
% endfor

  obj.tables = db.tables
  return setmetatable(obj, ${ClassName})
end

function ${ClassName}:select(table, ...)
  return self.db:select(table, ...)
end

function ${ClassName}:update(table, ...)
  return self.db:update(table, ...)
end

function ${ClassName}:insert(table, ...)
  return self.db:insert(table, ...)
end

function ${ClassName}:delete(table, ...)
  return self.db:delete(table, ...)
end

function ${ClassName}:exec(...)
  return self.db:exec(...)
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
