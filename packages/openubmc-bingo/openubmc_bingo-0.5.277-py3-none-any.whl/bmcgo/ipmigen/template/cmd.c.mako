<% import inflection %>
<% import re %>
#include "mdb_base.h"
#include "mcc/public.h"
#include "${inflection.underscore(package_name)}.h"

<%def name="message_decode_func(cmd, args, pointer_name)">
    gboolean allocated __attribute__((unused)) = FALSE;
    guint8 temp[IPMI_PAYLOAD_MAX + 1] = {0};
    if (n_data >= IPMI_PAYLOAD_MAX) {
        log_error("n_data bigger than %d, return NULL", IPMI_PAYLOAD_MAX - 1);
        return NULL;
    }
    if (${pointer_name} == NULL) {
        ${pointer_name} = g_new0(${cmd.name}_${pointer_name}, 1);
        allocated = TRUE;
    }
    if (n_data == 0 || data == NULL) {
        // 入参为空都不做任何处理，直接返回
        return ${pointer_name};
    }
    // 存入临时数组，避免内存读越界
    memcpy(temp, data, n_data);
    % if len(args) > 0:
    int pos_bit __attribute__((unused)) = 0;
    guint64 u64_tmp __attribute__((unused)) = 0;\
<%
    last_is_bit = False
    last_bit = -1
    now_bit = 0
%>
    % for arg in args:

    // >>> 开始处理${arg.data} >>>
        % if arg.len.endswith("b"):
            % if arg.ctype.c_len == 1:
    ${pointer_name}->${arg.data} = (temp[pos_bit / BIT_PER_BYTE] >> (pos_bit % BIT_PER_BYTE)) & (0xff >> (BIT_PER_BYTE - ${arg.bit_len}));
            % else:
                % if (last_bit // (8 * arg.ctype.c_len)) != (now_bit // (8 * arg.ctype.c_len)):
    u64_tmp = 0;
    // ${pointer_name}->${arg.data}需要复制${arg.ctype.c_len}字节再取值
<% bit_offset = 0 %>\
    for (int i = 0; i < ${arg.ctype.c_len}; i++) {
        ((guint8 *)&u64_tmp)[i] = temp[(pos_bit / BIT_PER_BYTE) + i];
    }
                % endif
                % if arg.ctype.c_len == 2:
    // ${arg.data}位宽为${arg.bit_len}, 从u64_tmp的${bit_offset}开始位取${arg.bit_len}位
    ${pointer_name}->${arg.data} = (u64_tmp >> ${bit_offset}) & ${hex(0xffff >> (16 - arg.bit_len))};
                % elif arg.ctype.c_len == 4:
    // ${arg.data}位宽为${arg.bit_len}, 从u64_tmp的${bit_offset}开始位取${arg.bit_len}位
    ${pointer_name}->${arg.data} = (u64_tmp >> ${bit_offset}) & ${hex(0xffffffff >> (32 - arg.bit_len))};
                % elif arg.ctype.c_len == 8:
    // ${arg.data}位宽为${arg.bit_len}, 从u64_tmp的${bit_offset}开始位取${arg.bit_len}位
    ${pointer_name}->${arg.data} = (u64_tmp >> ${bit_offset}) & ${hex(0xffffffffffffffff >> (64 - arg.bit_len))};
                % endif
<% bit_offset += arg.bit_len %>\
            % endif
    // 加上${arg.bit_len}
    pos_bit += ${arg.bit_len};\
<%
    last_is_bit = True
    last_bit = now_bit
    now_bit += arg.bit_len
%>
        % else:
            % if last_is_bit:
    pos_bit = ((pos_bit + BIT_PER_BYTE - 1) / BIT_PER_BYTE) * BIT_PER_BYTE;\
<%
    last_is_bit = False
    last_bit = -1
    now_bit = 0
%>
            % endif
            % if arg.base_type == "String *":
    ${pointer_name}->${arg.data} = (gchar *)(data + (pos_bit / BIT_PER_BYTE));
    pos_bit += (strlen(${pointer_name}->${arg.data}) + 1) * 8;
            % elif arg.base_type == "U8 *":
    ${pointer_name}->${arg.data} = (guint8 *)(data + (pos_bit / BIT_PER_BYTE));
                % if not re.match('^[1-9][0-9]+[bB]$', arg.len) and arg.len != '*':
                    % if arg.len_from_req == False:
    pos_bit += ${pointer_name}->${arg.len} * 8;
                    % else:
    pos_bit += ${pointer_name}->${arg.data}${arg.len} * 8;
                    % endif
                % endif
            % elif arg.base_type == "U8" or arg.base_type == "S8":
    ${pointer_name}->${arg.data} = temp[pos_bit / BIT_PER_BYTE];
    pos_bit += BIT_PER_BYTE;
            % else:
    // ${arg.data}位宽为${arg.bit_len}
    for (int i = 0; i < ${arg.bit_len}; i += BIT_PER_BYTE) {
        ((guint8 *)&${pointer_name}->${arg.data})[i / BIT_PER_BYTE] = temp[pos_bit / BIT_PER_BYTE];
        pos_bit += BIT_PER_BYTE;
    }
            % endif
        % endif
    % endfor
    gsize len = (pos_bit + BIT_PER_BYTE - 1) / BIT_PER_BYTE;
    if (len > n_data) {
        log_error("Memory overlay occurred, data size is %zu bigger than %zu", len, n_data);
        g_free(${pointer_name});
        return NULL;
    }
    % endif
    % for arg in args:
        % if arg.value is not None:
            % if arg.base_type.startswith("String"):
    if (strcmp(${pointer_name}->${arg.data}, "${arg.value}") != 0) {
            % else:
    if (${pointer_name}->${arg.data} != ${arg.value}) {
            % endif
        log_error("Filter ${arg.data} not match, need: ${arg.value}");
        if (allocated) {
            g_free(${pointer_name});
        }
        return NULL;
    }
        % endif
    % endfor
    return ${pointer_name};
</%def>\
<%def name="message_encode_func(cmd, args, pointer_name)">
    if (${pointer_name} == NULL) {
        return 0;
    }
    if (n_data == 0 || data == NULL) {
        return 0;
    }
    memset(data, 0, n_data);
    % if pointer_name == "rsp":
    if (rsp->${args[0].data} != 0) {
        data[0] = rsp->${args[0].data};
        return 1;
    }
    % endif
    gsize len = 0;
    % if len(args) > 0:
    guint64 u64_tmp __attribute__((unused)) = 0;
    int pos_bit __attribute__((unused)) = 0;\
<%
    last_is_bit = False
    last_bit = 0
    remain_bit = 0
%>
    % for arg in args:
        % if arg.len.endswith("b"):
    // ${arg.data}位宽为${arg.bit_len}
    u64_tmp = (guint64)${pointer_name}->${arg.data};
    // 取低${8 - last_bit}位再左移${last_bit}位
    data[pos_bit / BIT_PER_BYTE] |= (u64_tmp & ${hex(0xff >> last_bit)}) << ${last_bit};
            % if arg.bit_len <= (8 - last_bit):
    // bit位置加${arg.bit_len}位
    pos_bit += ${arg.bit_len};
<%
    remain_bit = 0
    last_bit = last_bit + arg.bit_len;
%>
            % else:
    // 右移${8 - last_bit}bit位以删除已赋值部分
    u64_tmp = u64_tmp >> ${8 - last_bit};
    // bit位置加${8 - last_bit}位
    pos_bit += ${8 - last_bit};\
<%
    remain_bit = arg.bit_len - (8 - last_bit)
    last_bit = 0
%>
            % endif
            % if remain_bit > 0:
                % for i in range(0, remain_bit, 8):
                    % if (remain_bit - i) < 8:
    // 右移${i}位后取${i + 8 - remain_bit}位
    data[(pos_bit + ${i}) / BIT_PER_BYTE] = (u64_tmp >> ${i}) & ${hex(0xff >> (i + 8 - remain_bit))};
                    % else:
    // 右移${i}位取
    data[(pos_bit + ${i}) / BIT_PER_BYTE] = (u64_tmp >> ${i}) & 0xff;
                    % endif
                % endfor
    // bit位置加${remain_bit}位
    pos_bit += ${remain_bit};
            % endif
<%
    last_is_bit = True
    last_bit += remain_bit % 8
    remain_bit = 0
%>\
        % else:
            % if last_is_bit == True:
    // 下一个成员不是位域，需要取整
    pos_bit = ((pos_bit + BIT_PER_BYTE - 1) / BIT_PER_BYTE) * BIT_PER_BYTE;\
<%
    last_is_bit = False
    last_bit = 0
%>
            % endif
            % if arg.base_type == "String *":
    if (${pointer_name}->${arg.data} != NULL) {
        len = strlen(${pointer_name}->${arg.data}) + 1;
        memmove_s(data + pos_bit / BIT_PER_BYTE, len, ${pointer_name}->${arg.data}, len);
        pos_bit += (len * BIT_PER_BYTE);
    } else {
        data[pos_bit / BIT_PER_BYTE] = '\0';
        pos_bit += 8;   // NULL转空字符串""
    }
            % elif arg.base_type == "U8 *":
                % if arg.len_from_req == False:
    ### BEGIN：为支持重复生成，只有版本号大于等于1的才需要判断长度是否为零
    % if version >= 1:
    if (${pointer_name}->${arg.len} > 0) {
        if (${pointer_name}->${arg.data} != NULL) {
            memmove_s(data + pos_bit / BIT_PER_BYTE, ${pointer_name}->${arg.len}, ${pointer_name}->${arg.data}, ${pointer_name}->${arg.len});
        } else {
            return 0;
        }
    }
    % else:
    if (${pointer_name}->${arg.data} != NULL) {
        memmove_s(data + pos_bit / BIT_PER_BYTE, ${pointer_name}->${arg.len}, ${pointer_name}->${arg.data}, ${pointer_name}->${arg.len});
    } else {
        return 0;
    }
    % endif
    ### END 版本号大于等于1的需要判断长度是否为零
    pos_bit += (${pointer_name}->${arg.len} * BIT_PER_BYTE);
                    % else:
    ### BEGIN：为支持重复生成，只有版本号大于等于1的才需要判断长度是否为零
    % if version >= 1:
    if (${pointer_name}->${arg.data}${arg.len} > 0) {
        if (${pointer_name}->${arg.data} != NULL) {
            memmove_s(data + pos_bit / BIT_PER_BYTE, ${pointer_name}->${arg.data}${arg.len}, ${pointer_name}->${arg.data}, ${pointer_name}->${arg.data}${arg.len});
        } else {
            return 0;
        }
    }
    % else:
    if (${pointer_name}->${arg.data} != NULL) {
        memmove_s(data + pos_bit / BIT_PER_BYTE, ${pointer_name}->${arg.data}${arg.len}, ${pointer_name}->${arg.data}, ${pointer_name}->${arg.data}${arg.len});
    } else {
        return 0;
    }
    % endif
    ### END 版本号大于等于1的需要判断长度是否为零
    pos_bit += (${pointer_name}->${arg.data}${arg.len} * BIT_PER_BYTE);
                % endif
            % elif arg.base_type == "U8" or arg.base_type == "S8":
    data[pos_bit / BIT_PER_BYTE] = (guint8)${pointer_name}->${arg.data};
    pos_bit += BIT_PER_BYTE;
            % else:
    // ${arg.data}位宽为${arg.bit_len}
    for (int i = 0; i < ${arg.bit_len}; i += BIT_PER_BYTE) {
        data[pos_bit / BIT_PER_BYTE] = ((guint8 *)&${pointer_name}->${arg.data})[i / BIT_PER_BYTE];
        pos_bit += BIT_PER_BYTE;
    }
            % endif
        % endif
    % endfor
    len = (pos_bit + BIT_PER_BYTE - 1) / BIT_PER_BYTE;
    if (len > n_data) {
        log_error("Memory overlay occurred, data size is %zu bigger than %zu", len, n_data);
        return 0;
    }
    % endif
    return len;
</%def>\
${cmd.name}_req *${cmd.name}_req_decode(gsize n_data, guint8 *data,
${" ".join("" for _ in range(len(cmd.name)))}                            ${cmd.name}_req *req)
{${message_decode_func(cmd, cmd.req_args, "req")}}

gsize ${cmd.name}_req_encode(gsize n_data, guint8 *data,
${" ".join("" for _ in range(len(cmd.name)))}                   const ${cmd.name}_req *req)
{${message_encode_func(cmd, cmd.req_args, "req")}}

${cmd.name}_rsp *${cmd.name}_rsp_decode(gsize n_data, guint8 *data,
${" ".join("" for _ in range(len(cmd.name)))}                            ${cmd.name}_rsp *rsp)
{${message_decode_func(cmd, cmd.rsp_args, "rsp")}}

gsize ${cmd.name}_rsp_encode(gsize n_data, guint8 *data,
${" ".join("" for _ in range(len(cmd.name)))}                   const ${cmd.name}_rsp *rsp)
{${message_encode_func(cmd, cmd.rsp_args, "rsp")}}
% if cmd.need_free_rsp:
void ${cmd.name}_rsp_free(${cmd.name}_rsp *rsp)
{
    % for arg in cmd.rsp_args:
        % if arg.base_type == "String *" or arg.base_type == "U8 *":
    g_free(rsp->${arg.data});
    rsp->${arg.data} = NULL;
        % endif
    % endfor
}
% endif

gint ${cmd.name}_call(const IpmiCmdInfo_Cli *object, const CallerContext *caller,
${" ".join("" for _ in range(len(cmd.name)))}            const ${cmd.name}_req *req, ${cmd.name}_rsp *rsp, GError **error)
{
    if (error == NULL) {
        log_error("Parameter error");
        return -1;
    }
    if (req == NULL || rsp == NULL) {
        *error = g_error_new(G_DBUS_ERROR, G_DBUS_ERROR_FAILED, "Parameter error");
        return -1;
    }
    guint8 data[IPMI_PAYLOAD_MAX + 1] = {0};
    IpmiCmdInfo_Process_Req payload = {};
    payload.n_Payload = ${cmd.name}_req_encode(sizeof(data), data, req);
    payload.Payload = data;
    payload.n_IpmiContext = 3;
    payload.IpmiContext = (guint8 *)"{}";
    // 权限用户等上下文信息
    if (caller == NULL) {
        caller = caller_context_static();
    }
    GVariant *gcontext = caller_context_build(caller);
    payload.Context = gcontext;
    IpmiCmdInfo_Process_Rsp response = {};
    gint ret = IpmiCmdInfo_Cli_Call_Process(object, &payload, &response, 1000, error);
    g_variant_unref(gcontext);
    if (ret != 0) {
        return ret;
    }
    if (response.n_Response >= IPMI_PAYLOAD_MAX) {
        *error = g_error_new(G_DBUS_ERROR, G_DBUS_ERROR_FAILED, "Response bigger than %d, len: %zu", IPMI_PAYLOAD_MAX - 1, response.n_Response);
        g_free(response.Response);
        return -1;
    }
    // 复制到缓存中，避免输入太少导致解码时越界
    memcpy(data, response.Response, response.n_Response);
    (void)${cmd.name}_rsp_decode(response.n_Response, data, rsp);
    g_free(response.Response);
    return 0;
}

static void ${cmd.name}_start(void)
{
    ${package_name} *cmds = ${package_name}_cmds();
    // 构造IPMI命令${cmd.name}对象名
    GString *str = g_string_new("");
    g_string_printf(str, "/bmc/kepler/IpmiCmds/%02x/%02x/%s", ${cmd.netfn}, ${cmd.cmd}, "${cmd.name}");
    cleanup_gfree gchar *object_name = g_string_free(str, FALSE);
    // 创建IPMI命令${cmd.name}对象
    const IpmiCmdInfo *obj = (const IpmiCmdInfo *)mcc_object_new(INTERFACE_IPMI_CMD_INFO,
        mcc_bus_name(), object_name, NULL);
    // 配置值
    IpmiCmdInfo_set_NetFn(obj, ${cmd.netfn});
    IpmiCmdInfo_set_Cmd(obj, ${cmd.cmd});
    /* "Default": 10, "Oem": 20, "Odm": 30, "EndUser": 40, "Max": 50 */
    IpmiCmdInfo_set_Priority(obj, ${cmd.priority});
    IpmiCmdInfo_set_Privilege(obj, ${cmd.privilege});
    IpmiCmdInfo_set_ServiceName(obj, mcc_bus_name());
    IpmiCmdInfo_set_Filter(obj, "${cmd.filter}");
% if version >= 3:
    IpmiCmdInfo_set_Sensitive(obj, ${"TRUE" if cmd.sensitive else "FALSE"});
% endif
% if version >= 3:
    gint32 value[2] = ${cmd.manufacturer};
    IpmiCmdInfo_set_Manufacturer(obj, 2, value);
% endif
    // 绑定IPMI命令的消息处理器
    mcc_object_set_bind(obj, (gpointer)&cmds->${cmd.name}, NULL);
    mcc_object_present_set(obj, TRUE);
}

static void __attribute__((constructor(CONSTRUCTOR_GDBUSPLUS_MODULE_PRIORITY))) ${cmd.name}_service(void)
{
    mdb_register_module(${cmd.name}_start, "${cmd.name}", STAGE_START);
}
