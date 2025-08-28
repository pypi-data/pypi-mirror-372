#include "mdb_base.h"
#include "mcc/public.h"
#include "${ipmi_cmds.name}.h"

static ${ipmi_cmds.package} ipmi_cmds = {
% for cmd in ipmi_cmds.cmds:
    .${cmd.name} = {
        .impl = NULL,
        .processer = {
            .req_decode = (ipmi_req_decode)${cmd.name}_req_decode,
            .req_encode = (ipmi_req_encode)${cmd.name}_req_encode,
            .rsp_decode = (ipmi_rsp_decode)${cmd.name}_rsp_decode,
            .rsp_encode = (ipmi_rsp_encode)${cmd.name}_rsp_encode,
    % if cmd.need_free_rsp:
            .rsp_free = (ipmi_rsp_free)${cmd.name}_rsp_free,
    % endif
        },
    },
% endfor
};

${ipmi_cmds.package} *${ipmi_cmds.package}_cmds(void)
{
    return &ipmi_cmds;
}
