#ifndef __${"_".join(xml.name.upper().split(".", -1))}_H__
#define __${"_".join(xml.name.upper().split(".", -1))}_H__

#include <glib-2.0/glib.h>
#include <glib-2.0/gio/gio.h>
#include "mdb_base.h"
#include "public/${xml.name}.h"
% for intf in xml.interfaces:
<% class_name = intf.class_name %>\

    % for prop in intf.properties:
        % if prop.ref_object:
            % if prop.signature.startswith("a"):
void ${class_name}_set_${prop.name}(const ${class_name} *object, MdbObject **value);
            % else:
void ${class_name}_set_${prop.name}(const ${class_name} *object, MdbObject *value);
            % endif
        % else:
void ${class_name}_set_${prop.name}(const ${class_name} *object, ${prop.server_in_args_str()});
        % endif
    % endfor

    % for signal in intf.signals:
        % for c in signal.comment.texts:
/* ${c} */
        % endfor
gboolean ${class_name}_${signal.name}_Signal(const ${class_name} *object, const gchar *destination, ${class_name}_${signal.name}_Msg *req, GError **error);
    % endfor

MdbInterface *${class_name}_interface(void);
#define INTERFACE_${intf.upper_name} ${class_name}_interface()
${class_name}_Properties *${class_name}_properties(void);
#define PROPERTIES_${intf.upper_name} ${class_name}_properties()
% endfor

#endif /* __${"_".join(xml.name.upper().split(".", -1))}_H__ */
