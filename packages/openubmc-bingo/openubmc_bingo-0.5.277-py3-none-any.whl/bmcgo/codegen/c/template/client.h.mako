#ifndef __${"_".join(xml.name.upper().split(".", -1))}_CLI_H__
#define __${"_".join(xml.name.upper().split(".", -1))}_CLI_H__

#include <glib-2.0/glib.h>
#include <glib-2.0/gio/gio.h>
#include "mdb_base.h"
#include "public/${xml.name}.h"
% for intf in xml.interfaces:
<% class_name = intf.class_name + "_Cli" %>
typedef ${intf.class_name} ${class_name};

    % for prop in intf.properties:
        % if not prop.ref_object:
int ${class_name}_set_${prop.name}(const ${class_name} *object, const CallerContext *ctx, ${prop.client_in_args_str()}, GError **error);
int ${class_name}_get_${prop.name}(const ${class_name} *object, const CallerContext *ctx, GError **error);
        % endif
    % endfor

    % for method in intf.methods:
int ${class_name}_Call_${method.name}(const ${class_name} *object, ${intf.class_name}_${method.name}_Req *req, ${intf.class_name}_${method.name}_Rsp *rsp, gint timeout, GError **error);
    % endfor

    % for signal in intf.signals:
typedef void (*${class_name}_${signal.name}_Signal)(const ${class_name} *object, const gchar *destination, ${intf.class_name}_${signal.name}_Msg *req, gpointer user_data);
guint ${class_name}_Subscribe_${signal.name}(${class_name}_${signal.name}_Signal handler,
    const gchar *bus_name, const gchar *object_path, const gchar *arg0, gpointer user_data);
void ${class_name}_Unsubscribe_${signal.name}(guint id);

    % endfor
MdbInterface *${class_name}_interface(void);
#define INTERFACE_CLI_${intf.upper_name} ${class_name}_interface()
${intf.class_name}_Properties *${class_name}_properties(void);
#define PROPERTIES_CLI_${intf.upper_name} *${class_name}_properties()
% endfor

#endif /* __${"_".join(xml.name.upper().split(".", -1))}_CLI_H__ */
