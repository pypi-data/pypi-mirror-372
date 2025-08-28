SCRIPT_DIR = $(PWD)/../../script
TEMPLATE_BIN = ${SCRIPT_DIR}/template.py
SEP_IPMI_MESSAGE_CMDS_BIN = ${SCRIPT_DIR}/sep_ipmi_message_cmds.py
LUA_FORMATER = ${SCRIPT_DIR}/lua_format.py
MDB_INTF_DIR = ${TEMP_DIR}/opt/bmc/apps/mdb_interface/
LATEST_MDB_INTF_DIR = ${TEMP_DIR}/opt/bmc/apps/latest_mdb_interface/
YAML_TO_JSON_BIN = ${SCRIPT_DIR}/yaml_to_json.py
BAK_LOCAL_DB_DIR = ${GEN_BAK_DIR}/${PROJECT_NAME}
MAJOR_VERSION_EQ_1 := $(shell [ $(MAJOR_VERSION) -eq 1 ] && echo true)

define get_proto_files
$(wildcard $(1)*.proto) $(foreach e, $(wildcard $(1)*), $(call get_proto_files, $(e)/))
endef
define get_proto_json_files
$(wildcard $(1)*.proto.json) $(foreach e, $(wildcard $(1)*), $(call get_proto_json_files, $(e)/))
endef

# 遍历读取当前目录的所有 .yaml 文件
define get_yaml_files
$(wildcard $(1)*.yaml) $(foreach e, $(wildcard $(1)*), $(call get_yaml_files, $(e)/))
endef
YAML_FILES_TMP = $(subst ${PROTO_DIR}/,,$(filter-out %errors.yaml, $(call get_yaml_files, ${PROTO_DIR}/)))
YAML_FILES = $(YAML_FILES_TMP:.yaml=)

YAML_FILES_CONF_TMP = $(subst ${CONF_DIR}/,,$(filter-out %errors.yaml, $(call get_yaml_files, ${CONF_DIR}/)))
YAML_FILES_CONF = $(YAML_FILES_CONF_TMP:.yaml=)

# 读取 interface 文件
INTERFACE_FILE = $(subst ${PROTO_OUT_DIR}/,, $(wildcard $(PROTO_OUT_DIR)/interface.proto.json))

# 读取 types 目录所有的文件
MESSAGE_JSON_FILES = $(foreach v, $(call get_proto_files, ${PROTO_DIR}/types/), $(subst ${PROTO_DIR}/,, $(v)))
MESSAGE_FILES = $(foreach v, $(MESSAGE_JSON_FILES), $(subst .proto,,$(v)))

# 读取 database 文件
DATABASE_FILE = $(subst ${PROTO_OUT_DIR}/,, $(wildcard $(PROTO_OUT_DIR)/database.proto.json))

# 遍历读取 routes 目录下的所有文件
RESTAPI_DIRS = routes
RESTAPI_JSON_DIR_FILES = $(foreach v, ${RESTAPI_DIRS}, $(call get_proto_json_files, ${PROTO_OUT_DIR}/${v}))
RESTAPI_JSON_FILES = $(foreach v, ${RESTAPI_JSON_DIR_FILES}, $(subst ${PROTO_OUT_DIR}/,, $(v)))
RESTAPI_FILES = $(foreach v, $(RESTAPI_JSON_FILES), $(subst .proto.json,,$(v)))

# 遍历读取 resource 目录下的所有文件
RESTAPI_RESOURCE_DIRS = resource
RESTAPI_RESOURCE_JSON_DIR_FILES = $(foreach v, ${RESTAPI_RESOURCE_DIRS}, $(call get_proto_json_files, ${PROTO_OUT_DIR}/${v}))
RESTAPI_RESOURCE_JSON_FILES = $(foreach v, ${RESTAPI_RESOURCE_JSON_DIR_FILES}, $(subst ${PROTO_OUT_DIR}/,, $(v)))
RESTAPI_RESOURCE_FILES = $(foreach v, $(RESTAPI_RESOURCE_JSON_FILES), $(subst .proto.json,,$(v)))

# 读取 ipmi 目录所有的文件
IPMI_JSON_FILES = $(foreach v, $(call get_proto_files, ${PROTO_DIR}/ipmi/), $(subst ${PROTO_DIR}/,, $(v)))
IPMI_FILES = $(foreach v, $(IPMI_JSON_FILES), $(subst .proto,,$(v)))

.PHONY: all service client message database datas datas_conf restapi restapi_resource ipmi model_message_json model_message service_message_json service_message client_messages_json client_messages types_message_json types_message feature_json feature impl_feature

default: all

define proto_json_to_lua
$(strip $(subst proto.json,lua,$(1)))
endef

define strip_proto_json
$(strip $(subst .proto.json,,$(1)))
endef

define MAKE_MESSAGE
ifeq ($(MAJOR_VERSION_EQ_1), true)
  $$(GEN_OUT_DIR)/$(1).lua: ${PROTO_OUT_DIR}/$(1).proto.json $${TEMPLATE_BIN} ${MAJOR_VERIONS_DIR}/v1/templates/apps/message.lua.mako utils/message.mako utils/enum.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/$(1).proto.json -f ${LUA_FORMATER} -t v1/templates/apps/message.lua.mako -o $$@
else
  $$(GEN_OUT_DIR)/$(1).lua: ${PROTO_OUT_DIR}/$(1).proto.json $${TEMPLATE_BIN} message.lua.mako utils/message.mako utils/enum.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/$(1).proto.json -f ${LUA_FORMATER} -t message.lua.mako -o $$@
endif
endef
$(foreach v, $(MESSAGE_FILES), $(eval $(call MAKE_MESSAGE,$(v))))
message: $(foreach v, $(MESSAGE_FILES), $(GEN_OUT_DIR)/$(v).lua)

define MAKE_DATAS
  $$(GEN_OUT_DIR)/$(1).lua: ${PROTO_OUT_DIR}/$(1).json $${TEMPLATE_BIN} datas.lua.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/$(1).json -f ${LUA_FORMATER} -t datas.lua.mako -o $$@
endef
$(foreach v, $(YAML_FILES), $(eval $(call MAKE_DATAS,$(v))))
datas: $(foreach v, $(YAML_FILES), $(GEN_OUT_DIR)/$(v).lua)

define MAKE_CONF_DATAS
  $$(GEN_OUT_DIR)/$(1).lua: ${CONF_DIR}/$(1).yaml $${TEMPLATE_BIN} datas.lua.mako
	@mkdir -p $$(dir $$@)
	python3 ${YAML_TO_JSON_BIN} -i ${CONF_DIR}/$(1).yaml -b ${CONF_DIR} -o ${PROTO_OUT_DIR}/$(1).json
	python3 $${TEMPLATE_BIN} -d ${CONF_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/$(1).json -f ${LUA_FORMATER} -t datas.lua.mako -o $$@
endef
$(foreach v, $(YAML_FILES_CONF), $(eval $(call MAKE_CONF_DATAS,$(v))))
datas_conf: $(foreach v, $(YAML_FILES_CONF), $(GEN_OUT_DIR)/$(v).lua)

define MAKE_RESTAPI
  $$(GEN_OUT_DIR)/$(1).lua: ${PROTO_OUT_DIR}/$(1).proto.json $${TEMPLATE_BIN} \
	controller.lua.mako utils/message.mako utils/validate.mako utils/enum.mako utils/imports.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/$(1).proto.json -f ${LUA_FORMATER} -t controller.lua.mako -o $$@
endef
$(foreach v, $(RESTAPI_FILES), $(eval $(call MAKE_RESTAPI,$(v))))
restapi: $(foreach v, $(RESTAPI_FILES), $(GEN_OUT_DIR)/$(v).lua)

$(foreach v, $(RESTAPI_RESOURCE_FILES), $(eval $(call MAKE_RESTAPI,$(v))))
restapi_resource: $(foreach v, $(RESTAPI_RESOURCE_FILES), $(GEN_OUT_DIR)/$(v).lua)

ifneq ($(wildcard ${MDS_DIR}/ipmi.json),)
${PROTO_OUT_DIR}/ipmi/ipmi.proto.json: ${MDS_DIR}/ipmi.json ${SCRIPT_DIR}/gen_ipmi_json.py
	@mkdir -p ${PROTO_OUT_DIR}/ipmi/
	python3 ${SCRIPT_DIR}/gen_ipmi_json.py -i ${MDS_DIR}/ipmi.json -v ${VERSION} -o $@
${GEN_OUT_DIR}/ipmi/ipmi.lua: ${PROTO_OUT_DIR}/ipmi/ipmi.proto.json ${TEMPLATE_BIN} ipmi.lua.mako
	@mkdir -p ${GEN_OUT_DIR}/ipmi/
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/ipmi/ipmi.proto.json -f ${LUA_FORMATER} -v ${VERSION} -t ipmi.lua.mako -o $@
$(GEN_OUT_DIR)/ipmi/ipmi_message.lua: ${PROTO_OUT_DIR}/ipmi/ipmi.proto.json ${TEMPLATE_BIN} ipmi_message.lua.mako
	@mkdir -p ${GEN_OUT_DIR}/ipmi/
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/ipmi/ipmi.proto.json -t ipmi_message.lua.mako -o $@
	python3 ${SEP_IPMI_MESSAGE_CMDS_BIN} ${MDS_DIR}/ipmi.json $(GEN_OUT_DIR)/ipmi/ipmi_message.lua $(GEN_OUT_DIR)/ipmi/cmds ${PROJECT_NAME} ${LUA_FORMATER}

ipmi: ${GEN_OUT_DIR}/ipmi/ipmi.lua  $(GEN_OUT_DIR)/ipmi/ipmi_message.lua
else

define MAKE_IPMI
  $$(GEN_OUT_DIR)/$(1).lua: ${PROTO_OUT_DIR}/$(1).proto.json $${TEMPLATE_BIN} ipmi.lua.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/$(1).proto.json -f ${LUA_FORMATER} -v ${VERSION} -t ipmi.lua.mako -o $$@
  $$(GEN_OUT_DIR)/$(1)_message.lua: ${PROTO_OUT_DIR}/$(1).proto.json $${TEMPLATE_BIN} ipmi_message.lua.mako
	@mkdir -p $$(dir $$@)
	python3 $${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR} -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/$(1).proto.json -f ${LUA_FORMATER} -t ipmi_message.lua.mako -o $$@
endef

$(foreach v, $(IPMI_FILES), $(eval $(call MAKE_IPMI,$(v))))
ipmi: $(foreach v, $(IPMI_FILES), $(GEN_OUT_DIR)/$(v).lua $(GEN_OUT_DIR)/$(v)_message.lua)

endif

${PROTO_OUT_DIR}/_model.json: ${SCRIPT_DIR}/merge_model.py
	python3 ${SCRIPT_DIR}/merge_model.py -i ${MDS_DIR}/model.json -o $@ -d ${MDB_INTF_DIR} -c ${SCRIPT_DIR}/../temp/check_cmd.json

ifeq ($(MAJOR_VERSION_EQ_1), true)
model_consistency_check: ${PROTO_OUT_DIR}/_model.json ${SCRIPT_DIR}/model_consistency_check.py
	python3 ${SCRIPT_DIR}/model_consistency_check.py -i ${PROTO_OUT_DIR}/_model.json -d ${LATEST_MDB_INTF_DIR}
else
model_consistency_check:
endif

ifeq ($(MAJOR_VERSION_EQ_1), true)
$(MDS_DIR)/modelx.json: ${PROTO_OUT_DIR}/_model.json
	mkdir -p $(@D)
	cp $< $@
modelx:${MDS_DIR}/modelx.json
else
modelx:
endif

${PROTO_OUT_DIR}/service.json: ${PROTO_OUT_DIR}/_model.json ${SCRIPT_DIR}/gen_intf_rpc_json.py
	python3 ${SCRIPT_DIR}/gen_intf_rpc_json.py -i ${PROTO_OUT_DIR}/_model.json -o $@ -s ${SERVICE_JSON_PATH} -p ${MDS_DIR}/ipmi.json

ifeq ($(MAJOR_VERSION_EQ_1), true)
${GEN_OUT_DIR}/service.lua: ${PROTO_OUT_DIR}/service.json ${TEMPLATE_BIN} \
	${MAJOR_VERIONS_DIR}/v1/templates/apps/service.lua.mako utils/validate.mako utils/imports.mako service_message message
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -v ${VERSION} -j ${PROTO_OUT_DIR}/json_types/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/service.json -f ${LUA_FORMATER} -t v1/templates/apps/service.lua.mako -o $@
else
${GEN_OUT_DIR}/service.lua: ${PROTO_OUT_DIR}/service.json ${TEMPLATE_BIN} \
  	service.lua.mako utils/validate.mako utils/imports.mako service_message message
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -v ${VERSION} -j ${PROTO_OUT_DIR}/json_types/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/service.json -f ${LUA_FORMATER} -t service.lua.mako -o $@
endif

service:${GEN_OUT_DIR}/service.lua

ifneq ($(wildcard ${MDS_DIR}/model.json),)
ifeq ($(MAJOR_VERSION_EQ_1), true)
${MDS_DIR}/schema.json: ${PROTO_OUT_DIR}/_model.json ${MAJOR_VERIONS_DIR}/v1/script/gen_schema.py
	python3 ${MAJOR_VERIONS_DIR}/v1/script/gen_schema.py -i ${PROTO_OUT_DIR}/_model.json -t ${MDS_DIR}/types.json -n ${PROJECT_NAME} -o $@
else
${MDS_DIR}/schema.json: ${PROTO_OUT_DIR}/_model.json ${SCRIPT_DIR}/gen_schema.py
	python3 ${SCRIPT_DIR}/gen_schema.py -i ${PROTO_OUT_DIR}/_model.json -n ${PROJECT_NAME} -o $@
endif

ifeq ($(MAJOR_VERSION_EQ_1), true)
${PROTO_OUT_DIR}/db_json.json: ${PROTO_OUT_DIR}/_model.json ${SCRIPT_DIR}/gen_db_json.py
	python3 ${SCRIPT_DIR}/gen_historical_local_db_json.py -i ${BAK_LOCAL_DB_DIR}/local_db.lua -o ${PROTO_OUT_DIR}/historical_local_db.json
	python3 ${SCRIPT_DIR}/gen_db_json.py -i ${PROTO_OUT_DIR}/_model.json -m ${PROTO_OUT_DIR}/historical_local_db.json -o $@
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/db_json.json -f ${LUA_FORMATER} -t v1/templates/apps/db.lua.mako -o ${GEN_OUT_DIR}/db.lua
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/local_db_json.json -f ${LUA_FORMATER} -t v1/templates/apps/local_db.lua.mako -o ${GEN_OUT_DIR}/local_db.lua
else
${PROTO_OUT_DIR}/db_json.json: ${PROTO_OUT_DIR}/_model.json ${SCRIPT_DIR}/gen_db_json.py
	python3 ${SCRIPT_DIR}/gen_historical_local_db_json.py -i ${BAK_LOCAL_DB_DIR}/local_db.lua -o ${PROTO_OUT_DIR}/historical_local_db.json
	python3 ${SCRIPT_DIR}/gen_db_json.py -i ${PROTO_OUT_DIR}/_model.json -m ${PROTO_OUT_DIR}/historical_local_db.json -o $@
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/db_json.json -f ${LUA_FORMATER} -t db.lua.mako -o ${GEN_OUT_DIR}/db.lua
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/local_db_json.json -f ${LUA_FORMATER} -t local_db.lua.mako -o ${GEN_OUT_DIR}/local_db.lua
endif

ifneq ($(wildcard ${MDS_DIR}/types.json),)
# types代码生成
types_message_json: ${TYPES_JSON_PATH} ${SCRIPT_DIR}/gen_rpc_msg_json.py
	mkdir -p ${PROTO_OUT_DIR}/model_types/
	python3 ${SCRIPT_DIR}/gen_rpc_msg_json.py -i ${TYPES_JSON_PATH} -o ${PROTO_OUT_DIR}/model_types/ -d ${MDB_INTF_DIR} -t

ifeq ($(MAJOR_VERSION_EQ_1), true)
types_message: types_message_json
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/model_types/ -n ${PROJECT_NAME} \
	-i ${PROTO_OUT_DIR}/model_types/def_types.proto.json -f ${LUA_FORMATER} -t v1/templates/apps/message.lua.mako \
	-o $(call proto_json_to_lua, ${GENERATE_OUT_DIR}/class/types/types.lua);
else
types_message: types_message_json
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/model_types/ -n ${PROJECT_NAME} \
	-i ${PROTO_OUT_DIR}/model_types/def_types.proto.json -f ${LUA_FORMATER} -t message.lua.mako \
	-o $(call proto_json_to_lua, ${GENERATE_OUT_DIR}/class/types/types.lua);
endif

endif

# model types代码生成
model_message_json: ${PROTO_OUT_DIR}/_model.json ${SCRIPT_DIR}/gen_rpc_msg_json.py
	mkdir -p ${PROTO_OUT_DIR}/model_types/
	python3 ${SCRIPT_DIR}/gen_rpc_msg_json.py -i ${PROTO_OUT_DIR}/_model.json -o ${PROTO_OUT_DIR}/model_types/ -d ${MDB_INTF_DIR} -p

ifeq ($(MAJOR_VERSION_EQ_1), true)
model_message: model_message_json
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/model_types/ -I def_types.proto.json), \
        python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/model_types/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/model_types/$x -f ${LUA_FORMATER} -t v1/templates/apps/message.lua.mako \
		-o $(call proto_json_to_lua, ${GENERATE_OUT_DIR}/class/types/$x);)
else
model_message: model_message_json
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/model_types/ -I def_types.proto.json), \
        python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/model_types/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/model_types/$x -f ${LUA_FORMATER} -t message.lua.mako \
		-o $(call proto_json_to_lua, ${GENERATE_OUT_DIR}/class/types/$x);)
endif

# 服务端代码生成
service_message_json: ${PROTO_OUT_DIR}/_model.json ${SCRIPT_DIR}/gen_rpc_msg_json.py
	@mkdir -p ${PROTO_OUT_DIR}/json_types/
	python3 ${SCRIPT_DIR}/gen_rpc_msg_json.py -i ${PROTO_OUT_DIR}/_model.json -o ${PROTO_OUT_DIR}/json_types/ -d ${MDB_INTF_DIR} -n ${PROJECT_NAME} -m

ifeq ($(MAJOR_VERSION_EQ_1), true)
service_message: service_message_json
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/json_types/),\
        python3 ${TEMPLATE_BIN} -v ${VERSION} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/json_types/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/json_types/$x -f ${LUA_FORMATER} -t v1/templates/apps/message.lua.mako \
		-o $(call proto_json_to_lua, ${GEN_OUT_DIR}/json_types/$x);)
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/device_types/),\
        python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/device_types/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/device_types/$x -f ${LUA_FORMATER} -t v1/templates/apps/message.lua.mako \
		-o $(call proto_json_to_lua, ${GEN_OUT_DIR}/device_types/$x);)
else
service_message: service_message_json
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/json_types/),\
        python3 ${TEMPLATE_BIN} -v ${VERSION} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/json_types/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/json_types/$x -f ${LUA_FORMATER} -t message.lua.mako \
		-o $(call proto_json_to_lua, ${GEN_OUT_DIR}/json_types/$x);)
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/device_types/),\
        python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/device_types/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/device_types/$x -f ${LUA_FORMATER} -t message.lua.mako \
		-o $(call proto_json_to_lua, ${GEN_OUT_DIR}/device_types/$x);)
endif

schema:  ${MDS_DIR}/schema.json
database: ${PROTO_OUT_DIR}/db_json.json

ifeq ($(MAJOR_VERSION_EQ_1), true)
${GENERATE_OUT_DIR}/class/model.lua: ${PROTO_OUT_DIR}/_model.json ${TEMPLATE_BIN} ${MAJOR_VERIONS_DIR}/v1/templates/apps/model.lua.mako
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -v ${VERSION} -j ${PROTO_OUT_DIR} -i ${PROTO_OUT_DIR}/_model.json -f ${LUA_FORMATER} -t v1/templates/apps/model.lua.mako -n ${PROJECT_NAME} -o $@
else
${GENERATE_OUT_DIR}/class/model.lua: ${PROTO_OUT_DIR}/_model.json ${TEMPLATE_BIN} model.lua.mako
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -v ${VERSION} -j ${PROTO_OUT_DIR} -i ${PROTO_OUT_DIR}/_model.json -f ${LUA_FORMATER} -t model.lua.mako -n ${PROJECT_NAME} -o $@
endif

model: ${GENERATE_OUT_DIR}/class/model.lua

VER_GE_9 := $(shell [ $(VERSION) -ge 9 ] && echo true)
ifeq ($(VER_GE_9), true)
feature_json: ${PROTO_OUT_DIR}/_model.json ${SCRIPT_DIR}/gen_feature_json.py
	mkdir -p ${PROTO_OUT_DIR}/features/
	rm -rf ${PLUGIN_TEMPLATE_DIR}
	python3 ${SCRIPT_DIR}/gen_feature_json.py -i ${PROTO_OUT_DIR}/_model.json -o ${PROTO_OUT_DIR}/features/ -n ${PROJECT_NAME} -f

feature: feature_json
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/features/),\
        python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/features/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/features/$x -f ${LUA_FORMATER} -t feature.lua.mako \
		-o $(call proto_json_to_lua, ${GEN_OUT_DIR}/features/$x);)

impl_feature: feature_json
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/features/),\
		mkdir -p ${PLUGIN_TEMPLATE_DIR}/$(call strip_proto_json, $x); \
        python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/features/$(call strip_proto_json, $x) -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/features/$x -f ${LUA_FORMATER} -t impl_feature.lua.mako \
		-o $(call proto_json_to_lua, ${PLUGIN_TEMPLATE_DIR}/$(call strip_proto_json, $x)/init.lua);)

else
feature_json:
feature:
impl_feature:
endif

ifeq ($(MAJOR_VERSION_EQ_1), true)
orm_classes:
else
orm_classes: ${PROTO_OUT_DIR}/db_json.json
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/db_json.json -f ${LUA_FORMATER} -t orm_classes.lua.mako -o ${GEN_OUT_DIR}/orm_classes.lua
endif

else
schema:
model:
database:
orm_classes:
feature_json:
feature:
impl_feature:
endif

ifneq ($(wildcard ${MDS_DIR}/service.json),)

${PROTO_OUT_DIR}/client.json: ${MDS_DIR}/service.json ${SCRIPT_DIR}/gen_intf_rpc_json.py
	python3 ${SCRIPT_DIR}/gen_intf_rpc_json.py -i ${MDS_DIR}/service.json -o $@ -d ${MDB_INTF_DIR}  -s ${SERVICE_JSON_PATH} -c

# 客户端代码生成
client_messages_json: ${MDS_DIR}/service.json ${SCRIPT_DIR}/gen_rpc_msg_json.py
	@mkdir -p ${PROTO_OUT_DIR}/json_types/
	python3 ${SCRIPT_DIR}/gen_rpc_msg_json.py -i ${MDS_DIR}/service.json -o ${PROTO_OUT_DIR}/json_types/ -d ${MDB_INTF_DIR} -n ${PROJECT_NAME} -x

ifeq ($(MAJOR_VERSION_EQ_1), true)
client_messages: client_messages_json
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/json_types/),\
        python3 ${TEMPLATE_BIN} -v ${VERSION} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/json_types/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/json_types/$x -f ${LUA_FORMATER} -t v1/templates/apps/message.lua.mako \
		-o $(call proto_json_to_lua, ${GEN_OUT_DIR}/json_types/$x);)
else
client_messages: client_messages_json
	@$(foreach x,$(shell ls $(PROTO_OUT_DIR)/json_types/),\
        python3 ${TEMPLATE_BIN} -v ${VERSION} -d ${PROTO_DIR} -j ${PROTO_OUT_DIR}/json_types/ -n ${PROJECT_NAME} \
		-i ${PROTO_OUT_DIR}/json_types/$x -f ${LUA_FORMATER} -t message.lua.mako \
		-o $(call proto_json_to_lua, ${GEN_OUT_DIR}/json_types/$x);)
endif

ifeq ($(MAJOR_VERSION_EQ_1), true)
${GEN_OUT_DIR}/client.lua : ${PROTO_OUT_DIR}/client.json ${TEMPLATE_BIN} \
  	${MAJOR_VERIONS_DIR}/v1/templates/apps/client.lua.mako utils/validate.mako utils/imports.mako client_messages message
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -v ${VERSION} -j ${PROTO_OUT_DIR}/json_types/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/client.json -f ${LUA_FORMATER} -t v1/templates/apps/client.lua.mako -o $@
else
${GEN_OUT_DIR}/client.lua : ${PROTO_OUT_DIR}/client.json ${TEMPLATE_BIN} \
  	client.lua.mako utils/validate.mako utils/imports.mako client_messages message
	python3 ${TEMPLATE_BIN} -d ${PROTO_DIR} -v ${VERSION} -j ${PROTO_OUT_DIR}/json_types/ -n ${PROJECT_NAME} -i ${PROTO_OUT_DIR}/client.json -f ${LUA_FORMATER} -t client.lua.mako -o $@
endif

client: ${GEN_OUT_DIR}/client.lua

endif

all: client service modelx message datas datas_conf restapi restapi_resource schema  model types_message model_message database ipmi orm_classes feature impl_feature model_consistency_check
