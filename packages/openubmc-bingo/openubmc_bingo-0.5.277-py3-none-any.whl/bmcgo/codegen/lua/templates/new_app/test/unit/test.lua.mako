${make_header('lua')}
<% camel_name=''.join(word.title() for word in project_name.split('_')) %>
loadfile(os.getenv('CONFIG_FILE'), 't', {package = package, os = os})()

local lu = require('luaunit')
local utils = require 'utils.core'
local logging = require 'mc.logging'

local current_file_dir = debug.getinfo(1).source:match('@?(.*)/')

utils.chdir(current_file_dir)
logging:setPrint(nil)
logging:setLevel(logging.INFO)

Test${camel_name}Cfg = {}

function Test${camel_name}Cfg:setupClass()
end

function Test${camel_name}Cfg:teardownClass()
end

os.exit(lu.LuaUnit.run())