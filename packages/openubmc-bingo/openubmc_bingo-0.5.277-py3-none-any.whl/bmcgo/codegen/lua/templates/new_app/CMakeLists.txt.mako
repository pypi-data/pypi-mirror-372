cmake_minimum_required(VERSION 3.14)
<% dollar="$" %>
project(${project_name})
find_package(PkgConfig REQUIRED)
pkg_search_module(GLIB REQUIRED glib-2.0)
pkg_search_module(GMODULE REQUIRED gmodule-2.0)

set(TARGET_LIB ${dollar}{PROJECT_NAME})
set(BUILD_DIR temp)

include(${dollar}{CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(APP_INSTALL_DIR opt/bmc/apps/${dollar}{PROJECT_NAME})
set(LUACLIB_INSTALL_DIR ${dollar}{APP_INSTALL_DIR}/luaclib)

install(DIRECTORY src/lualib DESTINATION ${dollar}{APP_INSTALL_DIR} OPTIONAL)
install(DIRECTORY include/ DESTINATION opt/bmc/lualib OPTIONAL)
install(DIRECTORY src/service DESTINATION ${dollar}{APP_INSTALL_DIR} OPTIONAL)
if (NOT ${dollar}{CMAKE_BUILD_TYPE} STREQUAL Release)
    install(DIRECTORY gen/debug/ DESTINATION ${dollar}{APP_INSTALL_DIR}/debug OPTIONAL)
    install(DIRECTORY src/debug/lualib DESTINATION ${dollar}{APP_INSTALL_DIR} OPTIONAL)
endif()
install(DIRECTORY gen/${dollar}{PROJECT_NAME}/ DESTINATION ${dollar}{APP_INSTALL_DIR} OPTIONAL)
install(DIRECTORY gen/class DESTINATION ${dollar}{APP_INSTALL_DIR} OPTIONAL)
install(FILES mds/schema.json DESTINATION ${dollar}{APP_INSTALL_DIR}/mds OPTIONAL)
install(FILES mds/service.json DESTINATION ${dollar}{APP_INSTALL_DIR}/mds OPTIONAL)
install(DIRECTORY user_conf/rootfs/ DESTINATION . USE_SOURCE_PERMISSIONS OPTIONAL)
install(FILES config.cfg DESTINATION ${dollar}{APP_INSTALL_DIR} OPTIONAL)
