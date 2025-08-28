#ifndef __${ipmi_cmds.name.upper()}_IPMI_H__
#define __${ipmi_cmds.name.upper()}_IPMI_H__
#include "client/bmc.kepler.CmdInfo.h"
#include "server/bmc.kepler.CmdInfo.h"
#pragma pack(1)
% for cmd in ipmi_cmds.cmds:

/* Notes: IPMI回调请求体如果有字符串指针("baseType": "String", "len": "*")的不能释放内存 */
typedef struct {
    % for arg in cmd.req_args:
    ${arg.c_declear_str};
    % endfor
} ${cmd.name}_req;

/* Notes: IPMI响应请求体如果有字符串指针("baseType": "String", "len": "*")的将由框架释放，请正确分配字符串 */
typedef struct {
    % for arg in cmd.rsp_args:
        % if arg.len_from_req:
    /* ${cmd.name}定义的${arg.data}成员长度为${arg.len}，来自于请求体${cmd.name}_req->${arg.len}，该成员不会做为响应的一部分返回 */
    guint8 ${arg.data}${arg.len};
        % endif
    ${arg.c_declear_str};
    % endfor
} ${cmd.name}_rsp;
${cmd.name}_req *${cmd.name}_req_decode(gsize n_data, guint8 *data, ${cmd.name}_req *req);
gsize ${cmd.name}_req_encode(gsize n_data, guint8 *data, const ${cmd.name}_req *req);
${cmd.name}_rsp *${cmd.name}_rsp_decode(gsize n_data, guint8 *data, ${cmd.name}_rsp *rsp);
gsize ${cmd.name}_rsp_encode(gsize n_data, guint8 *data, const ${cmd.name}_rsp *rsp);
% if cmd.need_free_rsp:
void ${cmd.name}_rsp_free(${cmd.name}_rsp *rsp);
% endif
gint ${cmd.name}_call(const IpmiCmdInfo_Cli *object, const CallerContext *caller,
    const ${cmd.name}_req *req, ${cmd.name}_rsp *rsp, GError **error);
typedef int (*${cmd.name}_impl)(const CallerContext *caller, const IpmiCmdCtx *ipmi_ctx,
    const ${cmd.name}_req *req, ${cmd.name}_rsp *rsp, GError **error);
#pragma pack()
% endfor

typedef struct {
% for cmd in ipmi_cmds.cmds:
    struct {
        ${cmd.name}_impl impl;
        IpmiCmdProcesser processer;
        gpointer *opaque;
    } ${cmd.name};
% endfor
} ${ipmi_cmds.package};

${ipmi_cmds.package} *${ipmi_cmds.package}_cmds(void);

#endif /* __${ipmi_cmds.name.upper()}_IPMI_H__ */
