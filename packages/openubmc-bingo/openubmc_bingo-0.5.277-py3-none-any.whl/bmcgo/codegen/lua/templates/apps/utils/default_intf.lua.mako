<%def name="render(default_path, ClassName, intf_cls, interface)">
## 生成默认对象的订阅和访问接口
${default_path} = ""
function ${ClassName}:Subscribe${intf_cls}()
    local org_freedesktop_dbus = require 'sd_bus.org_freedesktop_dbus'
    local MatchRule = org_freedesktop_dbus.MatchRule
    local sig = MatchRule.signal('InterfacesAdded'):with_path_namespace('/bmc')
    self.signal_slots[#self.signal_slots+1] = self:get_bus():match(sig, function(msg)
        local path, interfaces = msg:read()
        if interfaces['${interface}'] then
            ${default_path} = path
        end
    end)
    local mdb_service = require 'mc.mdb.mdb_service'
    local path_list = mdb_service.get_sub_paths(self:get_bus(), "/bmc", 10, {"${interface}"}).SubPaths
    for _, path in pairs(path_list) do
      ${default_path} = path
    end
end
table.insert(${ClassName}.subscriptions, 1, ${ClassName}.Subscribe${intf_cls})

function ${ClassName}:Get${intf_cls}Object()
  return mdb.get_object(self:get_bus(), ${default_path}, '${interface}')
end
</%def>

<%def name="add_subs(ClassName)">
## 生成默认对象的订阅和访问接口
${ClassName}.subscriptions = {}
function  ${ClassName}:SubscribeAll()
    if self.has_subscribe_all then
      return
    end

    for i = 1, #self.subscriptions do
      self.subscriptions[i](self)
    end

    self.has_subscribe_all = true
end
</%def>