PWD = $(shell pwd)
SCRIPT_DIR = $(PWD)/../script
PROTO_OUT_DIR = $(PWD)/../temp/proto

PROTO_PLUGIN_BIN = ${SCRIPT_DIR}/proto_plugin.py
YAML_TO_JSON_BIN = ${SCRIPT_DIR}/yaml_to_json.py

.PHONY: all protos yamls types json_path json_intf
default: all

# 遍历读取当前目录的所有 proto 文件
define get_proto_files
$(wildcard $(1)*.proto) $(foreach e, $(wildcard $(1)*), $(call get_proto_files, $(e)/))
endef
PROTO_FILES = $(subst $(PROTO_DIR),,$(call get_proto_files, ${PROTO_DIR}))

# 遍历读取当前目录的所有 .yaml 文件
define get_yaml_files
$(wildcard $(1)*.yaml) $(foreach e, $(wildcard $(1)*), $(call get_yaml_files, $(e)/))
endef
YAML_FILES_TMP = $(subst $(PROTO_DIR),,$(call get_yaml_files, ${PROTO_DIR}))
YAML_FILES = $(YAML_FILES_TMP:.yaml=)

# 编译 types.proto 文件
${SCRIPT_DIR}/types_pb2.py: types.proto
	protoc --python_out=${SCRIPT_DIR} -I$(PWD) types.proto

# 编译 ipmi_types.proto 文件
${SCRIPT_DIR}/ipmi_types_pb2.py: ipmi_types.proto
	protoc --python_out=${SCRIPT_DIR} -I$(PWD) ipmi_types.proto

types: ${SCRIPT_DIR}/types_pb2.py ${SCRIPT_DIR}/ipmi_types_pb2.py

define MAKE_PROTO
  $$(PROTO_OUT_DIR)/$(1).json: $(PROTO_DIR)$(1) $${PROTO_PLUGIN_BIN} $${SCRIPT_DIR}/types_pb2.py $${SCRIPT_DIR}/ipmi_types_pb2.py
	@mkdir -p $$(dir $$@)
	protoc --plugin=protoc-gen-custom=$$(PROTO_PLUGIN_BIN) --custom_out=$$(PROTO_OUT_DIR) -I$(PWD) -I$(PROTO_DIR) $(PROTO_DIR)$(1)
endef

$(foreach v, $(PROTO_FILES), $(eval $(call MAKE_PROTO,$(v))))

# 编译所有 .proto 文件
protos: $(foreach v, $(PROTO_FILES), $(PROTO_OUT_DIR)/$(v).json)

# 编译所有path .json 文件
define get_json_files
$(wildcard $(1)*.json) $(foreach e, $(wildcard $(1)*), $(call get_json_files, $(e)/))
endef
JSON_FILES_TMP = $(subst $(JSON_DIR),,$(call get_json_files, ${JSON_DIR}/path))
JSON_FILES = $(JSON_FILES_TMP:.json=)

JSON_BIN = ${SCRIPT_DIR}/gen_mdb_json.py
define MAKE_JSON
  $$(PROTO_OUT_DIR)/$(1).json: $(JSON_DIR)$(1).json $${JSON_BIN}
	@mkdir -p $$(dir $$@)
	python3 ${JSON_BIN} -i $(JSON_DIR)$(1).json -o $$@  
endef
$(foreach v, $(JSON_FILES), $(eval $(call MAKE_JSON,$(v))))
json_path: $(foreach v, $(JSON_FILES), $(PROTO_OUT_DIR)/$(v).json)


# 编译所有intf .json 文件

JSON_INTF_FILES_TMP = $(subst $(JSON_DIR),,$(call get_json_files, ${JSON_DIR}/intf))
JSON_INTF_FILES = $(JSON_INTF_FILES_TMP:.json=)

JSON_INTF_BIN = ${SCRIPT_DIR}/gen_intf_json.py
define MAKE_INTF_JSON
  $$(PROTO_OUT_DIR)/$(1).json: $(JSON_DIR)$(1).json $${JSON_BIN}
	@mkdir -p $$(dir $$@)
	python3 ${JSON_INTF_BIN} -i $(JSON_DIR)$(1).json -o $$@  -d ${JSON_DIR}
endef
$(foreach v, $(JSON_INTF_FILES), $(eval $(call MAKE_INTF_JSON,$(v))))
json_intf: $(foreach v, $(JSON_INTF_FILES), $(PROTO_OUT_DIR)/$(v).json)


# 编译所有 .yaml 文件
define MAKE_YAML
  $$(PROTO_OUT_DIR)/$(1).json: $(PROTO_DIR)$(1).yaml $${YAML_TO_JSON_BIN}
	@mkdir -p $$(dir $$@)
	python3 ${YAML_TO_JSON_BIN} -i $(PROTO_DIR)$(1).yaml -b ./ -o $$@
endef
$(foreach v, $(YAML_FILES), $(eval $(call MAKE_YAML,$(v))))
yamls: $(foreach v, $(YAML_FILES), $(PROTO_OUT_DIR)/$(v).json)


all: protos yamls json_path json_intf
