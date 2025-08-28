${make_header('lua')}
local Databases = require 'database'
local Col = require 'database.column'
<%namespace name="imports" file="utils/imports.mako"/>
${imports.render(root)}
<%
has_poweroff, has_reset, has_temporary = render_utils.check_local_per_type(root)
%>

local db_selector = {}

% if has_poweroff:
  <% ClassName = root['package'] + 'DatabasePoweroff' %>
  % for msg in root['data']:
    % if render_utils.table_name(msg) and render_utils.check_local_per_poweroff(msg):
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
    % if render_utils.table_name(msg) and render_utils.check_local_per_poweroff(msg):
---@field ${msg['name']} ${msg['name']}Table
    % endif
  % endfor

local ${ClassName} = {}
${ClassName}.__index = ${ClassName}

function ${ClassName}.new(path, datas)
  local db = Databases(path)
  local obj = {db = db}

  % for msg in root['data']:
    % if render_utils.table_name(msg) and render_utils.check_local_per_poweroff(msg):
  obj.${msg['name']} = db:Table('${render_utils.table_name(msg)}', {
      % for prop in msg['properties']:
    ${prop['name']} = Col.${render_utils.column_type(prop)}${render_utils.extend_field(prop)}:cid(${prop['id']})${render_utils.primary_key(prop)}${render_utils.unique(prop)}${render_utils.allow_null(prop)}${render_utils.max_len(prop)}${render_utils.default(msg['name'], prop)}${render_utils.deprecated(prop)},
      % endfor
    }):create_if_not_exist(datas and datas['${render_utils.table_name(msg)}'])
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
  % if render_utils.table_name(msg) and render_utils.check_local_per_poweroff(msg):
    % if render_utils.table_max_rows(msg) and render_utils.get_lua_codegen_version() >= 11:
  
function ${ClassName}:Register${msg['name']}TableMaxRowsCallback(cb)
  self.${msg['name']}.table_max_rows_cb = cb
end
    % endif
  % endif
% endfor

db_selector["poweroff"] = ${ClassName}.new
% endif

% if has_reset:
  <% ClassName = root['package'] + 'DatabaseReset' %>
  % for msg in root['data']:
    % if render_utils.table_name(msg) and render_utils.check_local_per_reset(msg):
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
    % if render_utils.table_name(msg) and render_utils.check_local_per_reset(msg):
---@field ${msg['name']} ${msg['name']}Table
    % endif
  % endfor

local ${ClassName} = {}
${ClassName}.__index = ${ClassName}

function ${ClassName}.new(path, datas)
  local db = Databases(path)
  local obj = {db = db}

  % for msg in root['data']:
    % if render_utils.table_name(msg) and render_utils.check_local_per_reset(msg):
  obj.${msg['name']} = db:Table('${render_utils.table_name(msg)}', {
      % for prop in msg['properties']:
    ${prop['name']} = Col.${render_utils.column_type(prop)}${render_utils.extend_field(prop)}:cid(${prop['id']})${render_utils.primary_key(prop)}${render_utils.unique(prop)}${render_utils.allow_null(prop)}${render_utils.max_len(prop)}${render_utils.default(msg['name'], prop)}${render_utils.deprecated(prop)},
      % endfor
    }):create_if_not_exist(datas and datas['${render_utils.table_name(msg)}'])
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
  % if render_utils.table_name(msg) and render_utils.check_local_per_reset(msg):
    % if render_utils.table_max_rows(msg) and render_utils.get_lua_codegen_version() >= 11:
  
function ${ClassName}:Register${msg['name']}TableMaxRowsCallback(cb)
  self.${msg['name']}.table_max_rows_cb = cb
end
    % endif
  % endif
% endfor

db_selector["reset"] = ${ClassName}.new
% endif

% if has_temporary:
  <% ClassName = root['package'] + 'DatabaseTemporary' %>
  % for msg in root['data']:
    % if render_utils.table_name(msg) and render_utils.check_local_per_temporary(msg):
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
    % if render_utils.table_name(msg) and render_utils.check_local_per_temporary(msg):
---@field ${msg['name']} ${msg['name']}Table
    % endif
  % endfor

local ${ClassName} = {}
${ClassName}.__index = ${ClassName}

function ${ClassName}.new(path, datas)
  local db = Databases(path)
  local obj = {db = db}

  % for msg in root['data']:
    % if render_utils.table_name(msg) and render_utils.check_local_per_temporary(msg):
  obj.${msg['name']} = db:Table('${render_utils.table_name(msg)}', {
      % for prop in msg['properties']:
    ${prop['name']} = Col.${render_utils.column_type(prop)}${render_utils.extend_field(prop)}:cid(${prop['id']})${render_utils.primary_key(prop)}${render_utils.unique(prop)}${render_utils.allow_null(prop)}${render_utils.max_len(prop)}${render_utils.default(msg['name'], prop)}${render_utils.deprecated(prop)},
      % endfor
    }):create_if_not_exist(datas and datas['${render_utils.table_name(msg)}'])
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
  % if render_utils.table_name(msg) and render_utils.check_local_per_temporary(msg):
    % if render_utils.table_max_rows(msg) and render_utils.get_lua_codegen_version() >= 11:
  
function ${ClassName}:Register${msg['name']}TableMaxRowsCallback(cb)
  self.${msg['name']}.table_max_rows_cb = cb
end
    % endif
  % endif
% endfor

db_selector["temporary"] = ${ClassName}.new
% endif

<% ClassName = root['package'] + 'Database' %>
local ${ClassName} = {}
${ClassName}.__index = ${ClassName}

function ${ClassName}.new(path, datas, type)
    return db_selector[type] and db_selector[type](path, datas) or nil
end

return ${ClassName}.new
