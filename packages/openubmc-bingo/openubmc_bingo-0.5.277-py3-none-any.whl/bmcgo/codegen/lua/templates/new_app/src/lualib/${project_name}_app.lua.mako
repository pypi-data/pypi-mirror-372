${make_header('lua')}

local class = require 'mc.class'
local service = require '${project_name}.service'

local ${project_name} = class(service)

function ${project_name}:ctor()

end

function ${project_name}:init()
    self.super.init(self)
end

return ${project_name}
