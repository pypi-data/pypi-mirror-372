#include "mdb_base.h"
#include "${xml.name}.h"

% for intf in xml.interfaces:
<% class_name = intf.class_name %>\
    % for prop in intf.properties:
        % if prop.private:
            % if len(prop.annotations) > 0:
/* annotation for the property ${prop.name} */
static GDBusAnnotationInfo ${class_name}_prop_${prop.name}_annotations_i[] = {
                % for anno in prop.annotations:
                    % for c in anno.comment.texts:
    /* ${c} */
                    % endfor
    {
        .ref_count = -1,
        .key = "${anno.name}",
        .value = "${anno.value}",
    },
                % endfor
};\
<% id = 0 %>
static GDBusAnnotationInfo *${class_name}_prop_${prop.name}_annotations[] = {
                % for anno in prop.annotations:
    &${class_name}_prop_${prop.name}_annotations_i[${id}],\
<% id = id + 1 %>
                % endfor
    NULL,
};
            % endif

        % for c in prop.comment.texts:
/* ${c} */
        % endfor
static GDBusPropertyInfo ${class_name}_property_${prop.name} = {
    .ref_count = -1,
    .name = "${prop.name}",
    .signature = "${prop.signature}",
    .flags = ${prop.access_flags},
    % if len(prop.annotations) > 0:
    .annotations = ${class_name}_prop_${prop.name}_annotations,
    % endif
};
        % endif
    % endfor

static ${class_name}_Properties _${class_name}_properties = {
<% id = 0 %>\
    % for prop in intf.properties:
    .${prop.name} = {
        .id = ${id},
<% id = id + 1 %>\
        .name = "${prop.name}",
        .offset = offsetof(${class_name}, ${prop.name}),
        .read_privilege = ${prop.read_privilege},
        .write_privilege = ${prop.write_privilege},
        % if prop.private:
        .info = &${class_name}_property_${prop.name},
        % else:
        .info = NULL, /* load from /usr/share/dbus-1/interfaces/${xml.name} by mdb_init */
        % endif
        .flags = ${prop.desc_flags}
    },
    % endfor
    .__reserved__ = {
        .name = NULL,       /* __reserved__ */
    },
};

const ${class_name}_Properties *${class_name}_properties_internal(void)
{
    return &_${class_name}_properties;
}

<%def name="message_decode_func(args, stru_name, msg_name)">
    if (${msg_name} == NULL) {
        ${msg_name} = g_new0(${stru_name}, 1);
    } else {
        memset(${msg_name}, 0, sizeof(${stru_name}));
    }
    // 如果parameters为空则返回一个初始化的结构体地址
    if (!parameters) {
        return ${msg_name};
    }
    gsize arg_id __attribute__((unused)) = 0;
        % for arg in args:
            % for line in arg.ctype.arg_decode:
    ${line.replace("<arg_name>", arg.name).replace("<req>", msg_name + "->")}
            % endfor
    arg_id++;
        % endfor
    return ${msg_name};
</%def>\
<%def name="message_encode_func(args, pointer_name)">
    % if len(args) > 0:
    if (!${pointer_name}) {
        return NULL;
    }
    % endif
    % for arg in args:
        %if arg.ctype.variant_type == "v":
    if (${pointer_name}->${arg.name} == NULL || g_strcmp0(g_variant_get_type_string(${pointer_name}->${arg.name}), "${arg.signature}") != 0) {
        return NULL;
    }
        % endif
    % endfor
    GVariant *tmp_v __attribute__((unused));
    GVariantBuilder builder;
    g_variant_builder_init(&builder, G_VARIANT_TYPE_TUPLE);
        % for arg in args:
            % for line in arg.ctype.arg_encode:
    ${line.replace("<arg_name>", arg.name).replace("<req>", pointer_name + "->")}
            % endfor
        % endfor
    return g_variant_builder_end(&builder);
</%def>\
<%def name="message_free_func(args, pointer_name)">
    % for arg in args:
        % for line in arg.ctype.arg_free:
    ${line.replace("<arg_name>", arg.name).replace("<req>", pointer_name + "->")}
        % endfor
    % endfor
    if (free_self) {
        g_free(${pointer_name});
    }
</%def>\
### 开始生成方法的请求体、响应体和处理函数
    % for method in intf.methods:
/* (服务端)将dbus接收到的消息转换成${class_name}_${method.name}_Req请求，配套Req_free释放 */
static ${class_name}_${method.name}_Req *${class_name}_${method.name}_Req_decode(GVariant *parameters, ${class_name}_${method.name}_Req *req)
{${message_decode_func(method.req_args, class_name + "_" + method.name + "_Req", "req")}}

/* (客户端)将${class_name}_${method.name}_Req请求转换成dbus需要发送的dbus消息(GVariant *)，无需调用Req_free */
static GVariant *${class_name}_${method.name}_Req_encode(${class_name}_${method.name}_Req *req)
{${message_encode_func(method.req_args, "req")}}

/* 释放${class_name}_${method.name}_Req请求结构体内容 */
static void ${class_name}_${method.name}_Req_free(${class_name}_${method.name}_Req *req, gboolean free_self)
{${message_free_func(method.req_args, "req")}}
/* (客户端)将dbus接收到的响应体转换成${class_name}_${method.name}_Rsp响应，配合Rsp_free释放 */
static ${class_name}_${method.name}_Rsp *${class_name}_${method.name}_Rsp_decode(GVariant *parameters, ${class_name}_${method.name}_Rsp *rsp)
{${message_decode_func(method.rsp_args, class_name + "_" + method.name + "_Rsp", "rsp")}}

/* (服务端)将方法回调函数生成的${class_name}_${method.name}_Rsp响应转换成dbus的响应(GVariant *)，无需调用Rsp_free */
static GVariant *${class_name}_${method.name}_Rsp_encode(${class_name}_${method.name}_Rsp *rsp)
{${message_encode_func(method.rsp_args, "rsp")}}

/* 释放${class_name}_${method.name}_Rsp响应结构体内容 */
static void ${class_name}_${method.name}_Rsp_free(${class_name}_${method.name}_Rsp *rsp, gboolean free_self)
{${message_free_func(method.rsp_args, "rsp")}}
    % endfor

static ${class_name}_MethodMsgProcesser _${class_name}_method_msg_processer = {
    % for method in intf.methods:
    .${method.name} = {
        .name = "${method.name}",
        .req_signature = "${method.req_signature()}",
        .req_decode = (mdb_message_decode)${class_name}_${method.name}_Req_decode,
        .req_encode = (mdb_message_encode)${class_name}_${method.name}_Req_encode,
        .req_free = (mdb_message_free)${class_name}_${method.name}_Req_free,
        .rsp_signature = "${method.rsp_signature()}",
        .rsp_decode = (mdb_message_decode)${class_name}_${method.name}_Rsp_decode,
        .rsp_encode = (mdb_message_encode)${class_name}_${method.name}_Rsp_encode,
        .rsp_free = (mdb_message_free)${class_name}_${method.name}_Rsp_free,
    },
    % endfor
    .__reserved__ = {
        .name = NULL,
    }
};

${class_name}_MethodMsgProcesser *${class_name}_method_msg_processer(void)
{
    return &_${class_name}_method_msg_processer;
}

    % for signal in intf.signals:
/* (客户端)将dbus接收到的消息转换成${class_name}_${signal.name}_Msg消息，配合Msg_free释放 */
static ${class_name}_${signal.name}_Msg *${class_name}_${signal.name}_Msg_decode(GVariant *parameters, ${class_name}_${signal.name}_Msg *msg)
{${message_decode_func(signal.args, class_name + "_" + signal.name + "_Msg", "msg")}}

/* (服务端)将${class_name}_${signal.name}_Msg转换成dbus需要发送的dbus消息(GVariant *)，无需释放 */
static GVariant *${class_name}_${signal.name}_Msg_encode(${class_name}_${signal.name}_Msg *req)
{${message_encode_func(signal.args, "req")}}

/* 释放${class_name}_${signal.name}_Msg消息内容 */
static void ${class_name}_${signal.name}_Msg_free(${class_name}_${signal.name}_Msg *msg, gboolean free_self)
{${message_free_func(signal.args, "msg")}}

    % endfor
static ${class_name}_SignalMsgProcesser _${class_name}_signal_msg_processer = {
    % for signal in intf.signals:
    .${signal.name} = {
        .name = "${signal.name}",
        .msg_signature = "${signal.msg_signature()}",
        .msg_decode = (mdb_message_decode)${class_name}_${signal.name}_Msg_decode,
        .msg_encode = (mdb_message_encode)${class_name}_${signal.name}_Msg_encode,
        .msg_free = (mdb_message_free)${class_name}_${signal.name}_Msg_free,
    },
    % endfor
    .__reserved__ = {
        .name = NULL,
    }
};

${class_name}_SignalMsgProcesser *${class_name}_signal_msg_processer(void)
{
    return &_${class_name}_signal_msg_processer;
}
static ${class_name}_Methods _${class_name}_methods = {
% for method in intf.methods:
    .${method.name} = {
        .name = "${method.name}",
        .privilege = ${method.privilege},
        .processer = (const MdbMethodMsgProcesser *)&_${class_name}_method_msg_processer.${method.name},
    },
% endfor
    .__reserved__ = {
        .name = NULL,
    },
};

${class_name}_Methods *${class_name}_methods(void)
{
    return &_${class_name}_methods;
}

% endfor
