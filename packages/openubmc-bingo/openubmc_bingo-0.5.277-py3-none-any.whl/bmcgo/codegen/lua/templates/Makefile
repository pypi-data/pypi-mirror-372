GENERATE_OUT_DIR = ${OUT_DIR}/gen
TEMPLATE_BIN = ${SCRIPT_DIR}/template.py
LUA_FORMATER = ${SCRIPT_DIR}/lua_format.py
MESSAGES_DIR := ${BUILD_DIR}/messages
MESSAGES_OUT_DIR := ${BUILD_DIR}/messages_gen

.PHONY: apps errors mdb dft_make debug_make

default: all

apps:
	@cd apps && make \
		GENERATE_OUT_DIR=${GENERATE_OUT_DIR} \
		PLUGIN_TEMPLATE_DIR=${TEMP_DIR}/plugin \
		SCRIPT_DIR=${SCRIPT_DIR} \
		MAJOR_VERIONS_DIR=${MAJOR_VERIONS_DIR} \
		PROTO_OUT_DIR=${PROTO_OUT_DIR} \
		PROTO_DIR=${PROTO_DIR} \
		PROJECT_NAME=${PROJECT_NAME} \
		VERSION=${VERSION} \
		MAJOR_VERSION=${MAJOR_VERSION} \
		RESTAPI_DIRS="${RESTAPI_DIRS}" \
		MDS_DIR=${MDS_DIR} \
		TEMP_DIR=${TEMP_DIR} \
		GEN_BAK_DIR=${GEN_BAK_DIR} \
		SERVICE_JSON_PATH=${MDS_DIR}/service.json \
		TYPES_JSON_PATH=${MDS_DIR}/types.json \
		OUT_DIR=${OUT_DIR} \
		GEN_OUT_DIR:=${GENERATE_OUT_DIR}/${PROJECT_NAME}

DFT_SERVICE_JSON_EXISTS := $(wildcard ${MDS_DIR}/service.json)
DFT_MODEL_JSON_EXISTS := $(wildcard ${MDS_DIR}/dft/model.json)
DFT_NAME = dft
ifneq ($(and $(DFT_SERVICE_JSON_EXISTS),$(DFT_MODEL_JSON_EXISTS)),)
dft_make:
	@cd apps && make \
		GENERATE_OUT_DIR=${GENERATE_OUT_DIR}/dft \
		PLUGIN_TEMPLATE_DIR=${TEMP_DIR}/dft/plugin \
		SCRIPT_DIR=${SCRIPT_DIR} \
		MAJOR_VERIONS_DIR=${MAJOR_VERIONS_DIR} \
		PROTO_OUT_DIR=${PROTO_OUT_DIR}/dft \
		PROTO_DIR=${PROTO_DIR} \
		PROJECT_NAME=${DFT_NAME} \
		VERSION=${VERSION} \
		MAJOR_VERSION=${MAJOR_VERSION} \
		RESTAPI_DIRS="${RESTAPI_DIRS}" \
		MDS_DIR=${MDS_DIR}/dft \
		TEMP_DIR=${TEMP_DIR} \
		GEN_BAK_DIR=${GEN_BAK_DIR} \
		SERVICE_JSON_PATH=${MDS_DIR}/dft/service.json \
		TYPES_JSON_PATH=${MDS_DIR}/dft/types.json \
		OUT_DIR=${OUT_DIR}/dft \
		GEN_OUT_DIR:=${GENERATE_OUT_DIR}/dft
else
dft_make:
endif

DEBUG_SERVICE_JSON_EXISTS := $(wildcard ${MDS_DIR}/service.json)
DEBUG_MODEL_JSON_EXISTS := $(wildcard ${MDS_DIR}/debug/model.json)
DEBUG_NAME = debug
ifneq ($(and $(DEBUG_SERVICE_JSON_EXISTS),$(DEBUG_MODEL_JSON_EXISTS)),)
debug_make:
	@cd apps && make \
		GENERATE_OUT_DIR=${GENERATE_OUT_DIR}/debug \
		PLUGIN_TEMPLATE_DIR=${TEMP_DIR}/debug/plugin \
		SCRIPT_DIR=${SCRIPT_DIR} \
		MAJOR_VERIONS_DIR=${MAJOR_VERIONS_DIR} \
		PROTO_OUT_DIR=${PROTO_OUT_DIR}/debug \
		PROTO_DIR=${PROTO_DIR} \
		PROJECT_NAME=${DEBUG_NAME} \
		VERSION=${VERSION} \
		MAJOR_VERSION=${MAJOR_VERSION} \
		RESTAPI_DIRS="${RESTAPI_DIRS}" \
		MDS_DIR=${MDS_DIR}/debug \
		TEMP_DIR=${TEMP_DIR} \
		GEN_BAK_DIR=${GEN_BAK_DIR} \
		SERVICE_JSON_PATH=${MDS_DIR}/debug/service.json \
		TYPES_JSON_PATH=${MDS_DIR}/debug/types.json \
		OUT_DIR=${OUT_DIR}/debug \
		GEN_OUT_DIR:=${GENERATE_OUT_DIR}/debug
else
debug_make:
endif

ifneq ($(wildcard ${MDS_DIR}/errors.json),)
${GENERATE_OUT_DIR}/${PROJECT_NAME}/errors.lua:
${GENERATE_OUT_DIR}/${PROJECT_NAME}/errors.lua: ${TEMPLATE_BIN} errors.lua.mako
	python3 ${TEMPLATE_BIN} -d ${PROTO_OUT_DIR} -i ${MDS_DIR}/errors.json -f ${LUA_FORMATER} -t errors.lua.mako -o $@
errors: ${GENERATE_OUT_DIR}/${PROJECT_NAME}/errors.lua
else
errors:
endif

define get_message_files
$(wildcard $(1)*.json) $(foreach e, $(wildcard $(1)*), $(call get_message_files, $(e)/))
endef

# 遍历读取 messages 目录所有的文件
MESSAGE_FILES = $(foreach v, $(call get_message_files, ${MESSAGES_DIR}/), $(subst ${MESSAGES_DIR}/,, $(v)))
MESSAGES = $(foreach v, $(MESSAGE_FILES), $(subst .json,,$(v)))

define MAKE_MESSAGE
  $$(MESSAGES_OUT_DIR)/$(1).lua: $${TEMPLATE_BIN} messages.lua.mako
	@mkdir -p $$(dir $$@)
	python3 ${TEMPLATE_BIN} -d ${PROTO_OUT_DIR} -i ${MESSAGES_DIR}/$(1).json -f ${LUA_FORMATER} -t messages.lua.mako -o $$@
endef
$(foreach v, $(MESSAGES), $(eval $(call MAKE_MESSAGE,$(v))))
messages: $(foreach v, $(MESSAGES), $(MESSAGES_OUT_DIR)/$(v).lua)

mdb:
	@cd apps && make \
		GENERATE_OUT_DIR=${GENERATE_OUT_DIR} \
		SCRIPT_DIR=${SCRIPT_DIR} \
		MAJOR_VERIONS_DIR=${MAJOR_VERIONS_DIR} \
		PROTO_OUT_DIR=${PROTO_OUT_DIR} \
		PROTO_DIR=${PROTO_DIR} \
		PROJECT_NAME=${PROJECT_NAME} \
		VERSION=${VERSION} \
		MAJOR_VERSION=${MAJOR_VERSION} \
		-f Makefile.mdb.mk

all: apps errors dft_make debug_make
