${make_header('lua')}

require 'app'
require 'callbacks/mc'
% if ipmi:
require 'callbacks/ipmi_cmd'
% endif
% for class_name in model:
require 'callbacks/classes/${class_name.lower()}'
% endfor
local utils_core = require 'utils.core'
local class = require 'mc.class'
local mc_admin = require 'mc.mc_admin'
local object_manage = require 'mc.mdb.object_manage'
local debug_manage = require 'mc.mdb.micro_component.debug'
local reboot_manage = require 'mc.mdb.micro_component.reboot'
% if ipmi:
local ipmi = require '${project_name}.ipmi.ipmi'
% endif
local factory = require '${project_name}.factory'
local app_service = require '${project_name}.service'

-- 继承service
local AppEntry = class(app_service)

function AppEntry:ctor()
end

function AppEntry:init()
    -- 1.注册回调
    -- 1) libmc公共接口实现
    -- 2) mds方法接口
    -- 3) ipmi回调
    -- 4) 属性信号监听回调
    self:ObjectMgmtCallbackRegister()
    self:ConfigMgmtCallbackRegister()
    self:RecoveryCallbackRegister()
    self:RebootCallbackRegister()
    self:DebugCallbackRegister()

    self:IpmiRegister()
    self:MethodRegister()

    -- 2.资源上树
    -- 在基类service中init将单例的资源上树
    self.super.init(self)

    -- 3.依赖检查
    self:check_dependencies()

    -- 4.用户初始化
    -- 调用用户代码初始化
    self:user_init()
end

function AppEntry:IpmiRegister()
% if ipmi:
% for ipmi_method in ipmi.get('cmds', []):
    self:register_ipmi_cmd(ipmi.${ipmi_method}, factory.get_obj_cb('ipmi_cmd', '${ipmi_method}'))
% endfor
% endif
end

function AppEntry:MethodRegister()
% if model:
% for class_name in model:
    % for interface in model[class_name].get('interfaces', []):
        % for method in model[class_name]['interfaces'][interface].get('methods', []):
<% interface_name = interface.split('.')[-1] %>
    % if interface_name == 'Default':
    <% pre_intf_name = interface.split('.')[-2] %>
    self:Impl${class_name}${pre_intf_name}${interface_name}${method}(factory.get_obj_cb('${class_name}', '${class_name}${pre_intf_name}${interface_name}${method}'))
    % else:
    <% unique_intf_name = render_utils.get_unique_intf_name(interface) %>
    self:Impl${class_name}${unique_intf_name}${method}(factory.get_obj_cb('${class_name}', '${class_name}${interface_name}${method}'))
    %endif
        % endfor
    % endfor
% endfor
% endif
end

function AppEntry:ObjectMgmtCallbackRegister()
    object_manage.on_add_object(self.bus, function (class_name, object, position)
        return factory.get_obj_cb(class_name, 'on_add_object')(class_name, object, position)
    end)
    object_manage.on_delete_object(self.bus, function (class_name, object, position)
        return factory.get_obj_cb(class_name, 'on_del_object')(class_name, object, position)
    end)
    object_manage.on_add_object_complete(self.bus, function (position)
        return factory.get_obj_cb('mc_callback', 'on_add_object_complete')(position)
    end)
    object_manage.on_delete_object_complete(self.bus, function (position)
        return factory.get_obj_cb('mc_callback', 'on_delete_object_complete')(position)
    end)
end

function AppEntry:ConfigMgmtCallbackRegister()
end

function AppEntry:RecoveryCallbackRegister()
end

function AppEntry:RebootCallbackRegister()
    reboot_manage.on_prepare(factory.get_obj_cb('mc_callback', 'on_reboot_prepare'))
    reboot_manage.on_action(factory.get_obj_cb('mc_callback', 'on_reboot_action'))
    reboot_manage.on_cancel(factory.get_obj_cb('mc_callback', 'on_reboot_cancel'))
end

function AppEntry:DebugCallbackRegister()
    debug_manage.on_dump(self.bus, factory.get_obj_cb('mc_callback', 'on_debug_dump'))
end

-- 依赖检查
function AppEntry:check_dependencies()
    local admin = mc_admin.new()
    admin:parse_dependency(utils_core.getcwd() .. '/mds/service.json')
    admin:check_dependency(self.bus)
end

-- 调用用户初始化
function AppEntry:user_init()
    factory.get_obj_cb('app', 'init')(self)

    factory.get_obj_cb('app', 'start')()
end

return AppEntry