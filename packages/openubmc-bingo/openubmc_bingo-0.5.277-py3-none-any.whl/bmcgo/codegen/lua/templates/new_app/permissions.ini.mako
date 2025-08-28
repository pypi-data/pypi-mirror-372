# syntax documentation
# format: name type mode uid gid
# name is the path to the file you want to create/modify
# type is the type of the file, being one of:
#   f: a regular file
#   d: a directory
#   r: a directory recursively
# mode are the usual permissions settings (only numerical values are allowed)
# name is the path to the file you want to create/modify
opt/bmc/apps/${project_name} d 550 0 0
opt/bmc/apps/${project_name} r 440 0 0
opt/bmc/apps/${project_name} rd 550 0 0
opt/bmc/apps/${project_name}/config.cfg f 640 0 0
opt/bmc/apps/${project_name}/mds d 750 0 0
opt/bmc/apps/${project_name}/mds r 640 0 0
etc/systemd/system/${project_name}.service f 640 0 0