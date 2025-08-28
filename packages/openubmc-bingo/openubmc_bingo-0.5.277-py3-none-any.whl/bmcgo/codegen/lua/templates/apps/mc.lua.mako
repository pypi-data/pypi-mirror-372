${make_header('lua')}

local class = require 'mc.class'
local factory = require '${project_name}.factory'
local mc_callback = class()

function mc_callback:on_add_object(class_name, object, position)

    return
end

function mc_callback:on_del_object(class_name, object, position)

    return
end

function mc_callback:on_add_object_complete(position)

    return
end

function mc_callback:on_delete_object_complete(position)

    return
end

function mc_callback:on_config_import(config_path)

    return
end

function mc_callback:on_config_export(config_path)

    return
end

function mc_callback:on_system_recovery()

    return
end

function mc_callback:on_system_backup()

    return
end

function mc_callback:on_reboot_prepare()

    return 0
end

function mc_callback:on_reboot_cancel()

    return
end

function mc_callback:on_reboot_action()

    return 0
end

function mc_callback:on_debug_setlevel(level)

    return
end

function mc_callback:on_debug_settype(type)

    return
end

function mc_callback:on_debug_dump(dump_path)

    return
end

factory.register_to_factory('mc_callback', mc_callback)
