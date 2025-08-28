#ifndef __${"_".join(xml.name.upper().split(".", -1))}_PUB_H__
#define __${"_".join(xml.name.upper().split(".", -1))}_PUB_H__
<% import inflection %>
#include <glib-2.0/glib.h>
#include <glib-2.0/gio/gio.h>
#include "mdb_base.h"
% for intf in xml.interfaces:

/* Interface ${intf.name} codegen start */
<% class_name = intf.class_name %>\
### 开始生成方法的请求体、响应体和处理函数
    % for method in intf.methods:
/* ${method.name}方法的请求体 */
typedef struct {
        % for arg in method.req_args:
            % for line in arg.ctype.render_in_args(arg.name, False).split(", ", -1):
    ${line};
            % endfor
        % endfor
} ${class_name}_${method.name}_Req;

/* ${method.name}方法的响应体 */
typedef struct {
        % for arg in method.rsp_args:
            % for line in arg.ctype.render_in_args(arg.name, False).split(", ", -1):
    ${line};
            % endfor
        % endfor
} ${class_name}_${method.name}_Rsp;

    % endfor
typedef struct {
% for method in intf.methods:
    struct {
        const gchar *const name;
        const gchar *const req_signature;
        mdb_message_decode req_decode;
        mdb_message_encode req_encode;
        mdb_message_free req_free;
        const gchar *const rsp_signature;
        mdb_message_decode rsp_decode;
        mdb_message_encode rsp_encode;
        mdb_message_free rsp_free;
    } ${method.name} ${method.deprecated_str};
% endfor
    MdbMethodMsgProcesser __reserved__;
} ${class_name}_MethodMsgProcesser;

typedef struct {
% for signal in intf.signals:
    struct {
        const gchar *const name;
        const gchar *const msg_signature;
        mdb_message_decode msg_decode;
        mdb_message_encode msg_encode;
        mdb_message_free msg_free;
    } ${signal.name} ${signal.deprecated_str};
% endfor
    MdbSignalMsgProcesser __reserved__;
} ${class_name}_SignalMsgProcesser;
### 开始生成信号的请求体
    % for signal in intf.signals:
typedef struct {
            % for arg in signal.args:
                % for line in arg.ctype.render_in_args(arg.name, False).split(", ", -1):
    ${line};
                % endfor
            % endfor
} ${class_name}_${signal.name}_Msg;
    % endfor

typedef struct {
% for prop in intf.properties:
    MdbProperty ${prop.name} ${prop.deprecated_str};
% endfor
    MdbProperty __reserved__;
} ${class_name}_Properties;

typedef struct {
    MdbBase _base;        /* Notice: property name can't be _base */
    char __reserved__[8]; /* 8bytes reserved space, can't be modified */
    % for prop in intf.properties:
        % if prop.ref_object:
            % if prop.signature.startswith("a"):
    MdbObject **${prop.name} ${prop.deprecated_str};
            % else:
    MdbObject *${prop.name} ${prop.deprecated_str};
            % endif
        % else:
    ${prop.struct_member()}
        % endif
    % endfor
} ${class_name};

% for method in intf.methods:
    % for c in method.comment.texts:
/* ${c} */
    % endfor
typedef int (*${class_name}_${method.name}_Method)(const ${class_name} *object, ${class_name}_${method.name}_Req *req, ${class_name}_${method.name}_Rsp *rsp, GError **error);
% endfor

typedef struct {
% for method in intf.methods:
    struct {
        const char *name;
        guint32 privilege;
        ${class_name}_${method.name}_Method handler;
        const MdbMethodMsgProcesser *processer;
        gpointer opaque;
    } ${method.name};
% endfor
    MdbMethod __reserved__;
} ${class_name}_Methods;

% for prop in intf.properties:
#define ${class_name}_${inflection.underscore(prop.name).upper()}_NAME "${prop.name}"
% endfor

#define INTERFACE_${intf.upper_name}_NAME "${intf.name}"
// internal function, Use PROPERTIES_${intf.upper_name} or PROPERTIES_CLI_${intf.upper_name} only
const ${class_name}_Properties *${class_name}_properties_internal(void);
${class_name}_Methods *${class_name}_methods(void);
${class_name}_SignalMsgProcesser *${class_name}_signal_msg_processer(void);
${class_name}_MethodMsgProcesser *${class_name}_method_msg_processer(void);
/* Interface ${intf.name} codegen finish */
% endfor

#endif /* __${"_".join(xml.name.upper().split(".", -1))}_PUB_H__ */
