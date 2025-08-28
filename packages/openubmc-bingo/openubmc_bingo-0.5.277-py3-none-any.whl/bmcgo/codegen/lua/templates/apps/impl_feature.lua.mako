${make_header('lua')}
local ${root['feature']} = require '${project_name}.features.${root['feature']}'.get_instance()

% for class_name, class_data in root.get('public', {}).items():
    % for intf_name, methods in class_data.items():
        % for method in methods:
-- 实现资源树方法的插件预处理方法
---@param obj Object
---@param ctx Context
---@param ... 资源树方法的入参
---@return Object 返回插件处理方法的入参，支持对插件预处理方法的入参做一些处理后传入插件处理方法
---@return Context 返回插件处理方法的入参，支持对插件预处理方法的入参做一些处理后传入插件处理方法
---@return ... 返回插件处理方法的入参，支持对插件预处理方法的入参做一些处理后传入插件处理方法
local function ${class_name}${intf_name}${method}Preprocess(obj, ctx, ...)

    return obj, ctx, ...
end

-- 实现资源树方法的插件处理方法
---@param obj Object
---@param ctx Context
---@param ... 资源树方法的入参
---@return response 资源树方法的出参，作为插件后置处理方法的入参传入插件后置处理方法
local function ${class_name}${intf_name}${method}Process(obj, ctx, ...)

end

-- 实现资源树方法的插件后置处理方法
---@param ... 1、如果实现了插件处理方法，则使用插件处理方法的出参 2、未实现插件处理方法时，使用资源树方法默认实现的出参
---@return ... 资源树方法的出参
local function ${class_name}${intf_name}${method}Postprocess(...)

    return ...
end

-- 入参分别为插件预处理、插件处理、插件后置处理方法的回调，实现相关回调后请将方法名填入，nil表示不进行相应处理
-- e.g. ${root['feature']}:Impl${class_name}${intf_name}${method}(${class_name}${intf_name}${method}Preprocess, ${class_name}${intf_name}${method}Process, ${class_name}${intf_name}${method}Postprocess)
${root['feature']}:Impl${class_name}${intf_name}${method}(nil, nil, nil)

        % endfor
    % endfor
% endfor

% for method in root.get('private', []):
-- 实现私有方法的插件预处理方法
---@param ... 私有方法的入参
---@return ... 返回插件处理方法的入参，支持对插件预处理方法的入参做一些处理后传入插件处理方法
local function ${method}Preprocess(...)

    return ...
end

-- 实现私有方法的插件处理方法
---@param ... 私有方法的入参
---@return response 私有方法的出参，作为插件后置处理方法的入参传入插件后置处理方法
local function ${method}Process(...)

end

-- 实现私有方法的插件后置处理方法
---@param ... 1、如果实现了插件处理方法，则使用插件处理方法的出参 2、未实现插件处理方法时，使用私有方法默认实现的出参
---@return ... 私有方法的出参
local function ${method}Postprocess(...)

    return ...
end

-- 入参分别为插件预处理、插件处理、插件后置处理方法的回调，实现相关回调后请将方法名填入，nil表示不进行相应处理
-- e.g. ${root['feature']}:Impl${method}(${method}Preprocess, ${method}Process, ${method}Postprocess)
${root['feature']}:Impl${method}(nil, nil, nil)

% endfor
