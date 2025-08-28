.PHONY: gen
<% dollar="$" %>
<% slash="\\" %>
PWD = ${dollar}(shell pwd)
PROTO_DIR=${dollar}{PWD}/proto
GENERATE_OUT_DIR=${dollar}{PWD}/gen
export ROOT_DIR = ${dollar}(PWD)/temp
export PROJECT_DIR = ${dollar}{PWD}
export LD_LIBRARY_PATH = ${dollar}{ROOT_DIR}/lib:${dollar}{ROOT_DIR}/lib64:${dollar}{ROOT_DIR}/usr/lib:${dollar}{ROOT_DIR}/usr/lib64
export CONFIG_FILE = ${dollar}{ROOT_DIR}/opt/bmc/libmc/config.cfg

LUA = ${dollar}(ROOT_DIR)/opt/bmc/skynet/lua
SKYNET = ${dollar}(ROOT_DIR)/opt/bmc/skynet/skynet

empty :=
space := ${dollar}(empty) ${dollar}(empty)

gen:
	@cd ${dollar}{TPL_DIR} && make ${slash}
        PROTO_DIR=${dollar}{PROTO_DIR} ${slash}
        BUILD_DIR=${dollar}{TPL_DIR}/temp ${slash}
        GENERATE_OUT_DIR=${dollar}{GENERATE_OUT_DIR} ${slash}
        PROTO_OUT_DIR=${dollar}{TPL_DIR}/temp/${dollar}{PROJECT_NAME} ${slash}
        PROJECT_NAME=${dollar}{PROJECT_NAME} ${slash}
        gen
