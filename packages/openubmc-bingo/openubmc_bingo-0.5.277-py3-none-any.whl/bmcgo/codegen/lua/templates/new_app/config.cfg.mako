include "/opt/bmc/libmc/config.cfg"

config:set_root("/")
config:set_start("${project_name}/service/main")
config:include_app("${project_name}")
config:done()
