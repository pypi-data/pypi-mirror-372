${make_header('lua')}

local org_freedesktop_dbus = require 'sd_bus.org_freedesktop_dbus'
local app_service = require '${project_name}.service'
local class = require 'mc.class'

-- 继承service
local sig = class(app_service)
local MatchRule = org_freedesktop_dbus.MatchRule

function sig:SubscriptionSigNotify(cb)
    local slots = {}
    local sig_properties_changed = MatchRule.signal('PropertiesChanged',
        'org.freedesktop.DBus.Properties')
    slots[#slots + 1] = self.bus:match(sig_properties_changed, cb) -- cb的参数是msg，由组件解析
    self.match_slots = slots
end

return sig