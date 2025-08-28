include("$CONFIG_FILE")

config:init_integration_test_dirs()
config:set_start("test_${project_name}")
config:include_app('${project_name}')
config:done()

TEST_DATA_DIR = 'test/integration/.test_temp_data/'
test_apps_root = 'test/integration/apps/'