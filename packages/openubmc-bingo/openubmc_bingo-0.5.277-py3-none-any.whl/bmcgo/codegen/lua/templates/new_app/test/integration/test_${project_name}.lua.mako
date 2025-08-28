${make_header('lua')}
local skynet = require 'skynet'
require 'skynet.manager'
local log = require 'mc.logging'
local utils = require 'mc.utils'
local test_common = require 'test_common.utils'

local function prepare_test_data()
    local test_data_dir = skynet.getenv('TEST_DATA_DIR')
    os.execute('mkdir -p ' .. test_data_dir)
    os.execute('mkdir -p ' .. '/tmp/test_dump')
end

local function clear_test_data(exit_test)
    log:info('clear test data')
    local test_data_dir = skynet.getenv('TEST_DATA_DIR')
    if not exit_test then
        return utils.remove_file(test_data_dir)
    end

    skynet.timeout(0, function()
        skynet.sleep(20)
        skynet.abort()
        utils.remove_file(test_data_dir)
        utils.remove_file('/tmp/test_dump')
    end)
end

local function test_${project_name}()
    log:info('================ test start ================')

    log:info('================ test complete ================')
end

skynet.start(function()
    clear_test_data(false)
    prepare_test_data()
    test_common.dbus_launch()
    skynet.uniqueservice('main')
    skynet.fork(function()
        local ok, err = pcall(test_${project_name})
        clear_test_data(true)
        if not ok then
            error(err)
        end
    end)
end)
