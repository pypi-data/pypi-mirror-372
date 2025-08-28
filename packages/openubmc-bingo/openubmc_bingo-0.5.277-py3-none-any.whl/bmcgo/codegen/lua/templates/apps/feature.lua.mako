${make_header('lua')}
local class = require 'mc.class'
local singleton = require 'mc.singleton'
local feature = require 'mc.plugin.feature'

local ${root['feature']} = class(feature)

function ${root['feature']}:ctor()

end

% for class_name, class_data in root.get('public', {}).items():
    % for intf_name, methods in class_data.items():
        % for method in methods:
function ${root['feature']}:${class_name}${intf_name}${method}(...)
    return self:call('${class_name}${intf_name}${method}', ...)
end

function ${root['feature']}:Impl${class_name}${intf_name}${method}(preprocess_cb, process_cb, postprocess_cb)
    self:implement('${class_name}${intf_name}${method}', preprocess_cb, process_cb, postprocess_cb)
end

        % endfor
    % endfor
% endfor
% for method in root.get('private', []):
function ${root['feature']}:${method}(...)
    return self:call('${method}', ...)
end

function ${root['feature']}:Impl${method}(preprocess_cb, process_cb, postprocess_cb)
    self:implement('${method}', preprocess_cb, process_cb, postprocess_cb)
end

% endfor
return singleton(${root['feature']})

