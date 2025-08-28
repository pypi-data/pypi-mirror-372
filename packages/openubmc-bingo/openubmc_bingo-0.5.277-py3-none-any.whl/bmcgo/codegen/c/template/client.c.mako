#include "mdb_base.h"
#include "${xml.name}.h"

% for intf in xml.interfaces:
<% class_name = intf.class_name + "_Cli"
method_processer = "_" + intf.class_name + "_method_msg_processer"
properties = "_" + intf.class_name + "_properties"
signal_processer = "_" + intf.class_name + "_signal_msg_processer"
%>\
static ${intf.class_name}_MethodMsgProcesser *${method_processer} = NULL;
static ${intf.class_name}_Properties ${properties};
static ${intf.class_name}_SignalMsgProcesser *${signal_processer} = NULL;

    % for prop in intf.properties:
        % if not prop.ref_object:
        % for c in prop.comment.texts:
/* ${c} */
        % endfor
int ${class_name}_set_${prop.name}(const ${class_name} *object, const CallerContext *ctx, ${prop.client_in_args_str()}, GError **error)
{
    cleanup_unref GVariant *_value = ${prop.ctype.args_write_remote_declear.replace("<arg_name>", prop.name)};
    return mdb_impl.set((MdbObject *)object, ctx, &${properties}.${prop.name}, _value, error);
}
int ${class_name}_get_${prop.name}(const ${class_name} *object, const CallerContext *ctx, GError **error)
{
    GVariant *out_val = NULL;
    gint ret = mdb_impl.get((MdbObject *)object, ctx, &${properties}.${prop.name}, &out_val, error);
    if (ret != 0) {
        return ret;
    }
    g_variant_unref(out_val);
    return 0;
}

    % endif
    % endfor
    % for method in intf.methods:
/*
 * Call dbus method: ${method.name}
        % for arg in method.req_args:
            % if len(arg.comment.texts) > 0:
 *   @in_${arg.name}: ${" ".join(arg.comment.texts)}
            % else:
 *   @in_${arg.name}: method input
            % endif
        % endfor
        % for arg in method.rsp_args:
            % if len(arg.comment.texts) > 0:
 *   @out_${arg.name}: ${" ".join(arg.comment.texts)}
            % else:
 *   @out_${arg.name}: method output
            % endif
        % endfor
 *
% for c in method.comment.texts:
 * ${c}
% endfor
 */
int ${class_name}_Call_${method.name}(const ${class_name} *object, ${intf.class_name}_${method.name}_Req *req, ${intf.class_name}_${method.name}_Rsp *rsp, gint timeout, GError **error)
{
    return mdb_impl.call_method((MdbObject *)object, (const MdbMethodMsgProcesser *)&${method_processer}->${method.name},
                                 req, rsp, timeout, error);
}
    % endfor

static MdbObject *_${class_name}_create(const gchar *obj_name, gpointer opaque);
/*
 * interface: ${intf.name}
% for c in intf.comment.texts:
 * ${c}
% endfor
 */
static MdbInterface _${class_name}_interface = {
    .create = _${class_name}_create,
    .is_remote = 1,
    .privilege = ${intf.privilege},
    .name = "${intf.name}",
    .class_name = "${intf.class_name}",
    .properties = (MdbProperty *)&${properties},
    .methods = NULL,
    .interface = NULL, /* load from usr/share/dbus-1/interfaces/${xml.name} by mdb_init */
};

MdbObject *_${class_name}_create(const gchar *obj_name, gpointer opaque)
{
    ${class_name} *obj = g_new0(${class_name}, 1);
    (void)memcpy_s(obj->_base.magic, strlen(MDB_MAGIC) + 1, MDB_MAGIC, strlen(MDB_MAGIC) + 1);
    obj->_base.lock = g_new0(GRecMutex, 1);
    g_rec_mutex_init(obj->_base.lock);
    obj->_base.name = g_strdup(obj_name);
    obj->_base.intf = &_${class_name}_interface;
    obj->_base.opaque = opaque;
    return (MdbObject *)obj;
}
    % for signal in intf.signals:
/*
 * Send dbus signal: ${signal.name}
        % for c in signal.comment.texts:
 * ${c}
        % endfor
 */
guint ${class_name}_Subscribe_${signal.name}(${class_name}_${signal.name}_Signal handler, const gchar *bus_name,
    const gchar *object_path, const gchar *arg0, gpointer user_data)
{
    if (handler == NULL) {
        log_error("parameter error, handler is NULL");
        return 0;
    }
    return mdb_impl.subscribe_signal(&_${class_name}_interface, bus_name, (const MdbSignalMsgProcesser *)&${signal_processer}->${signal.name},
                                     object_path, arg0, (mdb_signal_handler)handler, user_data);
}

void ${class_name}_Unsubscribe_${signal.name}(guint id)
{
    return mdb_impl.unsubscribe_signal(id);
}

% endfor

MdbInterface *${class_name}_interface(void)
{
    return &_${class_name}_interface;
}

${intf.class_name}_Properties *${class_name}_properties(void)
{
    return &${properties};
}

static void __attribute__((constructor(CONSTRUCTOR_REGISTER_INTERFACE_PRIORITY))) ${class_name}_register(void)
{
    // 从公共库中复制信号处理函数
    ${signal_processer} = ${intf.class_name}_signal_msg_processer();

    // 从公共库中复制方法处理函数
    ${method_processer} = ${intf.class_name}_method_msg_processer();

    // 从公共库中复制属性信息
    (void)memcpy_s(&${properties}, sizeof(${properties}),${intf.class_name}_properties_internal(), sizeof(${properties}));

    mdb_register_interface(&_${class_name}_interface,
                           "${xml.introspect_xml_sha256}",
                           "/usr/share/dbus-1/interfaces/${xml.name}.xml");
}
% endfor
