#include "mdb_base.h"
#include "${xml.name}.h"
#include "public/${xml.name}.h"

% for intf in xml.interfaces:
<%
class_name = intf.class_name
method_processer = "_" + class_name + "_method_msg_processer"
properties = "_" + class_name + "_properties"
signal_processer = "_" + class_name + "_signal_msg_processer"
%>\
static ${class_name}_SignalMsgProcesser *${signal_processer} = NULL;
static ${class_name}_Properties ${properties} = {NULL};
static ${class_name}_Methods *_${class_name}_methods = NULL;

    % for prop in intf.properties:
        % for c in prop.comment.texts:
/* ${c} */
        % endfor
        % if prop.ref_object:
            % if prop.signature.startswith("a"):
void ${class_name}_set_${prop.name}(const ${class_name} *object, MdbObject **value)
{
    mdb_set_array_object(object, &${properties}.${prop.name}, value);
}
            % else:
void ${class_name}_set_${prop.name}(const ${class_name} *object, MdbObject *value)
{
    mdb_set_object(object, &${properties}.${prop.name}, value);
}
            % endif
        % else:
void ${class_name}_set_${prop.name}(const ${class_name} *object, ${prop.server_in_args_str()})
{
    cleanup_unref GVariant *_value = ${prop.ctype.args_write_remote_declear.replace("<arg_name>", "value")};
    (void)mdb_impl.set((MdbObject *)object, NULL, &${properties}.${prop.name}, _value, NULL);
}
    % endif

    % endfor
    % for signal in intf.signals:
/*
 * Signal: ${signal.name}
        % for c in signal.comment.texts:
 * ${c}
        % endfor
 */
gboolean ${class_name}_${signal.name}_Signal(const ${class_name} *object, const gchar *destination, ${class_name}_${signal.name}_Msg *msg, GError **error)
{
    return mdb_impl.emit_signal((MdbObject *)object, destination, (const MdbSignalMsgProcesser *)&${signal_processer}->${signal.name}, msg, error);
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
    .create = _${intf.class_name}_create,
    .is_remote = 0,
    .privilege = ${intf.privilege},
    .name = "${intf.name}",
    .class_name = "${intf.class_name}",
    .properties = (MdbProperty *)&${properties},
    .interface = NULL,  /* load from usr/share/dbus-1/interfaces/${xml.name} by mdb_init */
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

MdbInterface *${class_name}_interface(void)
{
    return &_${class_name}_interface;
}

${class_name}_Properties *${class_name}_properties(void)
{
    return &${properties};
}

static void __attribute__((constructor(CONSTRUCTOR_REGISTER_INTERFACE_PRIORITY))) ${class_name}_register(void)
{
    ${signal_processer} = ${class_name}_signal_msg_processer();
    _${class_name}_methods = ${class_name}_methods();
    _${class_name}_interface.methods = (MdbMethod *)_${class_name}_methods;
    (void)memcpy_s(&${properties}, sizeof(${properties}), ${intf.class_name}_properties_internal(), sizeof(${properties}));

    mdb_register_interface(&_${class_name}_interface,
                           "${xml.introspect_xml_sha256}",
                           "/usr/share/dbus-1/interfaces/${xml.name}.xml");
}
% endfor
