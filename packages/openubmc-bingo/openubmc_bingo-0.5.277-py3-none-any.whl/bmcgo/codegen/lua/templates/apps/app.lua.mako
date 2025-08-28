${make_header('lua')}

local factory = require '${project_name}.factory'
local class = require 'mc.class'
local log = require 'mc.logging'

local app = class()

function app:init()

    return
end

function app:start()

    return
end

factory.register_to_factory('app', app)
