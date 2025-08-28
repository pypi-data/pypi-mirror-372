[Unit]
Description=${project_name} service
After=dbus.service
Requires=dbus.service

[Service]
User=root
Restart=always
RestartSec=1
StartLimitInterval=0
EnvironmentFile=/dev/shm/dbus/.dbus
Environment="ROOT_DIR="
Environment="PROJECT_DIR="
WorkingDirectory=/opt/bmc/apps/${project_name}
ExecStart=/opt/bmc/skynet/skynet /opt/bmc/apps/${project_name}/config.cfg

[Install]
WantedBy=multi-user.target
