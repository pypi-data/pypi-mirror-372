${make_header('lua')}

local skynet = require 'skynet'
require 'skynet.manager'
local log = require 'mc.logging'
local app_entry = require '${project_name}.entry'

local CMD = {}

function CMD.exit()
    skynet.timeout(0, function()
        log:info('${project_name} service exit')
        skynet.exit()
    end)
end

skynet.start(function()
    skynet.uniqueservice('sd_bus')
    skynet.register('${project_name}')
    app_entry.new()
    skynet.dispatch('lua', function(_, _, cmd, ...)
        local f = assert(CMD[cmd])
        skynet.ret(skynet.pack(f(...)))
    end)
end)
