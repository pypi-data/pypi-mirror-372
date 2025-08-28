${make_header('lua')}
local M = {}

% for name, rows in root.items():
M.${name} = ${utils_py.format_value(rows, '')}
% endfor

return M