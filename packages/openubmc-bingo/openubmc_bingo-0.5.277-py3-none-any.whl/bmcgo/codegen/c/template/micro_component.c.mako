#include "mcc/public.h"
#include "server/bmc.kepler.MicroComponent.h"

#define MCC_BUS_NAME "bmc.kepler.${mds["name"]}"

#define MCC_APP_NAME "${mds["name"]}"

static void micro_component_start(void)
{
    const MicroComponent *component = mcc_object_new(INTERFACE_MICRO_COMPONENT, mcc_bus_name(),
        "/bmc/kepler/${mds["name"]}/MicroComponent", NULL);
    if (component == NULL) {
        log_error("Create object failed, interface: %s,"
            "object: /bmc/kepler/${mds["name"]}/MicroComponent",
            INTERFACE_MICRO_COMPONENT_NAME);
    } else {
        mcc_object_present_set(component, TRUE);
        MicroComponent_set_Author(component, "${mds.get("author", "Huawei")}");
        MicroComponent_set_Description(component, "${mds.get("description", "").replace('"', '\\\"')}");
        MicroComponent_set_Pid(component, (gint32)getpid());
        MicroComponent_set_Version(component, "${mds["version"]}");
        MicroComponent_set_License(component, "${mds.get("license", "Mulan PSL v2")}");
        MicroComponent_set_Name(component, "${mds["name"]}");
        MicroComponent_set_Status(component, "Starting");
    }
}

static void __attribute__((constructor(150))) micro_component_init(void)
{
    mdb_register_module(micro_component_start, "micro_component", STAGE_START);
    mcc_bus_name_set(MCC_BUS_NAME);
}
