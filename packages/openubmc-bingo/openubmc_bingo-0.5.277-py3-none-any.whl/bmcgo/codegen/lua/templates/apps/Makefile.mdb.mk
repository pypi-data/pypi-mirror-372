OUT_DIR = $(PWD)/../../build
PROTO_OUT_DIR = $(OUT_DIR)/proto
SCRIPT_DIR = $(PWD)/../../script
TEMPLATE_BIN = ${SCRIPT_DIR}/template.py
GENERATE_OUT_DIR := ${OUT_DIR}/gen
PROTO_DIR = $(PWD)/../../proto
LUA_FORMATER = ${SCRIPT_DIR}/lua_format.py
JSON_PATH_DIR = ${PROTO_OUT_DIR}/path
JSON_INTF_DIR = ${PROTO_OUT_DIR}/intf

define get_proto_json_files
$(wildcard $(1)*.proto.json) $(foreach e, $(wildcard $(1)*), $(call get_proto_json_files, $(e)/))
endef

define get_dir_name
$(shell echo $(dir $(1))|awk -F '/' '{ print $$(NF-1) }')
endef

# 遍历读取 mdb 目录所有的文件
MDB_JSON_FILES = $(foreach v, $(filter-out %message.proto.json %messages.proto.json %enums.proto.json, $(call get_proto_json_files, ${PROTO_OUT_DIR}/)), $(subst ${PROTO_OUT_DIR}/,, $(v)))
MDB_FILES = $(foreach v, $(MDB_JSON_FILES), $(subst .proto.json,,$(v)))

define get_json_files
$(wildcard $(1)*.json) $(foreach e, $(wildcard $(1)*), $(call get_json_files, $(e)/))
endef

MDB_PAHT_JSON_FILES = $(foreach v, $(call get_json_files, ${JSON_PATH_DIR}/), $(subst ${JSON_PATH_DIR}/,, $(v)))
MDB_PATH_FILES = $(foreach v, $(MDB_PAHT_JSON_FILES), $(subst .json,,$(v)))
MDB_INTF_JSON_FILES = $(foreach v, $(call get_json_files, ${JSON_INTF_DIR}/), $(subst ${JSON_INTF_DIR}/,, $(v)))
MDB_INTF_FILES = $(foreach v, $(MDB_INTF_JSON_FILES), $(subst .json,,$(v)))

.PHONY: all mdb mdb_interface

default: all

# 实现资源树对象注册代码自动生成
define MAKE_MDB_INTERFACE_JSON
  $$(GENERATE_OUT_DIR)/$$(subst index,$(call get_dir_name, $(1)),$(1))Interface.lua: ${JSON_INTF_DIR}/$(1).json $${TEMPLATE_BIN} mdb_interface.lua.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${JSON_INTF_DIR} -n ${PROJECT_NAME} -i ${JSON_INTF_DIR}/$(1).json -f ${LUA_FORMATER} -t mdb_interface.lua.mako -o $$@
endef
$(foreach v, $(MDB_INTF_FILES), $(eval $(call MAKE_MDB_INTERFACE_JSON,$(v))))
mdb_interface: $(foreach v, $(MDB_INTF_FILES), $(GENERATE_OUT_DIR)/$(subst index,$(call get_dir_name, $(v)),$(v))Interface.lua)

define MAKE_MDB_JSON
  $$(GENERATE_OUT_DIR)/$$(subst index,init,$(1)).lua: ${JSON_PATH_DIR}/$(1).json $${TEMPLATE_BIN} mdb.lua.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${JSON_PATH_DIR} -n ${PROJECT_NAME} -i ${JSON_PATH_DIR}/$(1).json -f ${LUA_FORMATER} -t mdb.lua.mako -o $$@
endef
$(foreach v, $(MDB_PATH_FILES), $(eval $(call MAKE_MDB_JSON,$(v))))
mdb: $(foreach v, $(MDB_PATH_FILES), $(GENERATE_OUT_DIR)/$(subst index,init,$(v)).lua)

define MAKE_MESSAGE
  $$(GENERATE_OUT_DIR)/$(1).lua: ${PROTO_OUT_DIR}/$(1).proto.json $${TEMPLATE_BIN} message.lua.mako utils/message.mako utils/enum.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/$(1).proto.json -f ${LUA_FORMATER} -t message.lua.mako -o $$@
endef
MDB_MESSAGE_JSON_FILES = $(foreach v, $(filter %message.proto.json %messages.proto.json %enums.proto.json, $(call get_proto_json_files, ${PROTO_OUT_DIR}/mdb)), $(subst ${PROTO_OUT_DIR}/,, $(v)))
MDB_MESSAGE_FILES = $(foreach v, $(MDB_MESSAGE_JSON_FILES), $(subst .proto.json,,$(v)))
$(foreach v, $(MDB_MESSAGE_FILES), $(eval $(call MAKE_MESSAGE,$(v))))
mdb_message: $(foreach v, $(MDB_MESSAGE_FILES), $(GENERATE_OUT_DIR)/$(v).lua)

all: mdb mdb_interface mdb_message

