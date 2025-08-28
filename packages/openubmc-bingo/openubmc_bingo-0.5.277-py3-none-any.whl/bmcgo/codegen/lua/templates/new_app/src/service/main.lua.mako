${make_header('lua')}

require 'skynet.manager'
local skynet = require 'skynet'
local logging = require 'mc.logging'
local ${project_name}_app = require '${project_name}_app'

local CMD = {}

function CMD.exit()
    logging:notice('${project_name} service exit')
end

skynet.start(function()
    skynet.uniqueservice('sd_bus')
    skynet.register('${project_name}')
    local ok, err = pcall(${project_name}_app.new)
    if not ok then
        logging:error('${project_name} start failed, err: %s', err)
    end
    skynet.dispatch('lua', function(_, _, cmd, ...)
        local f = assert(CMD[cmd])
        skynet.ret(skynet.pack(f(...)))
    end)
end)