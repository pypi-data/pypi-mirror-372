${make_header('lua')}
local c_object = require 'mc.orm.object'

local orm_classes = {}

% if utils_py.check_db_open(project_name):
function orm_classes.init(db)
% for msg in root['data']:
  % if render_utils.table_name(msg):
    orm_classes.${msg['name']} = c_object("${msg['name']}")
  % endif
% endfor
end
% endif

return orm_classes