import os
import stat
import urllib3
% if pkg.is_maintain:
import shutil
% endif
from conans import ConanFile, CMake
% if pkg.is_maintain:
from conans import tools
from conans.util.files import mkdir
from conan.tools.files import patch as apply_patch
from conans.errors import ConanException
% endif

urllib3.disable_warnings()

# 构建时由工具自动生成到业务仓，做为conanfile.py的基类参与组件构建
# 如需要调试，请修改模板文件（目录中存在python版本号、bmcgo集成开发环境应用名称，请适配）：
#   ~/.local/lib/python3.8/site-packages/bmcgo/component/template/conanbase.py.mako


class ConanBase(ConanFile):
    name = "${pkg.name}"
% if not pkg.is_maintain:
    version = "${pkg.version}"
% endif
    settings = "os", "compiler", "build_type", "arch"
    license = "Mulan PSL v2"
    generators = "cmake"
    language = "${language}"
    _cmake = None
    _codegen_version = ${codegen_version}
% if not pkg.is_maintain:
    scm = {
        "type": "git",
        "url": "${remote_url}",
        "revision": "auto"
    }
% endif
    options = {
        "asan": [True, False],
        "gcov": [True, False],
        "manufacture": [True, False],
    % for op, ctx in pkg.design_options.items():
        "${op}": [${",".join(("\"" + i + "\"") if isinstance(i, str) else str(i) for i in ctx["option"])}],
    % endfor
    }
    default_options = {
        "asan": False,
        "gcov": False,
        "manufacture": False,
    % for op, ctx in pkg.design_options.items():
        "${op}": ${("\"" + ctx["default"] + "\"") if isinstance(ctx["default"], str) else str(ctx["default"])},
    % endfor
    }

    def generate(self):
        file_descriptor = os.open("conan_toolchain.cmake", os.O_RDWR | os.O_CREAT, stat.S_IWUSR | stat.S_IRUSR)
        file_handler = os.fdopen(file_descriptor, "w")
        file_handler.write("add_compile_definitions(\"_FORTIFY_SOURCE=2\")\n")
        file_handler.close()

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export(self):
        self.copy("mds/service.json")
        self.copy("conanbase.py")

% if pkg.is_maintain:
    def export_sources(self):
        patches = self.conan_data.get("patches", {}).get(self.version, [])
        for patch in patches:
            patch_file = patch.get("patch_file")
            if patch_file is None:
                continue
            # 与export_conandata_patches方法不同点：所有patches将从recipes_folder/../pacthes读取
            src = os.path.join(self.recipe_folder, "..", patch_file)
            dst = os.path.join(self.export_sources_folder, patch_file)
            mkdir(os.path.dirname(dst))
            shutil.copy2(src, dst)

    def source(self):
        git = tools.Git(verify_ssl=False)
        git.clone(**self.conan_data["sources"][self.version])
% endif

    % if len(pkg.build_dependencies) > 0 or len(pkg.test_dependencies) > 0:
    def requirements(self):
        uc = ""
        if self.user and self.channel:
            if self.channel == "dev":
                uc = f"@{self.user}/rc"
            else:
                uc = f"@{self.user}/{self.channel}"
        # 编译依赖
        % for build_dep in pkg.build_dependencies:
            % if "@" in build_dep:
        self.requires("${build_dep}")
            % else:
        self.requires(f"${build_dep}{uc}")
            % endif
        % endfor

    % endif

    def _codegen(self):
        from bmcgo.component.gen import GenComp
        args = ["-s", "mds/service.json"]
        gen = GenComp(args)
        gen.run(self._codegen_version)

    def _new_cmake(self):
        return CMake(self)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = self._new_cmake()
        self._cmake.definitions["BUILD_MANUFACTURE"] = self.options.manufacture
        if self.settings.build_type == "Dt":
            self._cmake.definitions["ENABLE_TEST"] = "ON"

% if len(pkg.design_options) > 0:
    % for op, _ in pkg.design_options.items():
        self._cmake.definitions["CONAN_DEFS_${op.upper()}"] = self.options.${op}
    % endfor
% endif
        # 向CMAKE传递版本号信息
        version = self.version.split(".")
        if len(version) >= 1:
            self._cmake.definitions["PACKAGE_VERSION_MAJOR"] = version[0]
        if len(version) >= 2:
            self._cmake.definitions["PACKAGE_VERSION_MINOR"] = version[1]
        if len(version) >= 3:
            self._cmake.definitions["PACKAGE_VERSION_REVISION"] = version[2]
        # 设置额外编译选项或者重定义CFLAGS CXXFLAGS,也可以设置其他开关
        # 示例: os.environ['CFLAGS'] = f"{os.getenv('CFLAGS')} -fPIE"

        if self.settings.arch == "armv8" or self.settings.arch == "x86_64":
            self._cmake.definitions["CMAKE_INSTALL_LIBDIR"] = "usr/lib64"
        else:
            self._cmake.definitions["CMAKE_INSTALL_LIBDIR"] = "usr/lib"

        if self.options.asan:
            print("Enable asan flags")
            flag = " -fsanitize=address -fsanitize-recover=address,all -fno-omit-frame-pointer -fno-stack-protector -O0"
            os.environ['CFLAGS'] = os.getenv('CFLAGS') + flag
            os.environ['CXXFLAGS'] = os.getenv('CXXFLAGS') + flag
        if self.options.gcov:
            print("Enable gcov flags")
            os.environ['CFLAGS'] = f"{os.getenv('CFLAGS')} -ftest-coverage -fprofile-arcs"
            os.environ['CXXFLAGS'] = f"{os.getenv('CXXFLAGS')} -ftest-coverage -fprofile-arcs"

        # 配合generate添加宏定义
        self._cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = "conan_toolchain.cmake"
        # rpath配置
        self._cmake.definitions["CMAKE_SKIP_BUILD_RPATH"] = True
        self._cmake.definitions["CMAKE_SKIP_RPATH"] = True
        self._cmake.definitions["CMAKE_SKIP_INSTALL_RPATH"] = True
        self._cmake.definitions["CMAKE_BUILD_WITH_INSTALL_RPATH"] = False
        self._cmake.definitions["CMAKE_INSTALL_RPATH_USE_LINK_PATH"] = False
        self._cmake.configure(args=["--no-warn-unused-cli"])
        return self._cmake

% if pkg.is_maintain:
    @staticmethod
    def _get_patch_changed_files(patch_file):
        files = {}
        for line in open(patch_file):
            if not line.startswith("diff --git"):
                continue
            line = line.strip()
            chunk = line.split()
            a_file = chunk[-2][2:]
            b_file = chunk[-1][2:]
            files[a_file] = b_file
        return files

    def _revise_renamed_files(self, changed_files):
        for a_file, b_file in changed_files.items():
            if a_file != b_file:
                if a_file != "/dev/null" and b_file != "/dev/null":
                    os.rename(a_file, b_file)
                    cmd = f"git rm -f {a_file}"
                    self.run(cmd)
                elif a_file != "/dev/null":
                    cmd = f"git rm -f {a_file}"
                    self.run(cmd)
                    continue
            cmd = f"git add {b_file}"
            self.run(cmd)

%endif
    def build(self):
% if pkg.is_maintain:
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            patch_file = patch.get("patch_file")
            if not patch_file:
                continue
            real_path = os.path.join(self.folders.base_source, patch_file)
            print(f"Start patch file {patch_file}")
            changed_files = self._get_patch_changed_files(real_path)
            try:
                apply_patch(self, patch_file=real_path)
                self._revise_renamed_files(changed_files)
                cmd = f"git commit -m \"{patch_file}\""
                self.run(cmd)
            except ConanException:
                # 尝试还原文件修改
                for a_file, b_file in changed_files.items():
                    cmd = f"git checkout -- {a_file}"
                    self.run(cmd, ignore_errors=True)
                    cmd = f"git checkout -- {b_file}"
                    self.run(cmd, ignore_errors=True)
                cmd = "git am " + real_path
                self.run(cmd)
% endif
        if self.language != "c":
            return
        self._codegen()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        if os.path.isfile("permissions.ini"):
            self.copy("permissions.ini")
        if os.path.isfile("mds/model.json"):
           self.copy("model.json", src="mds", dst="include/mds")
        if os.path.isfile("mds/service.json"):
           self.copy("service.json", src="mds", dst="include/mds")
        if os.path.isdir("build"):
            self.copy("*", src="build", dst="include")
        if os.path.isdir("mds"):
            self.copy("*", src="mds", dst="usr/share/doc/openubmc/${pkg.name}/mds")
        if os.path.isdir("docs"):
            self.copy("*", src="docs", dst="usr/share/doc/openubmc/${pkg.name}/docs")
        self.copy("*.md", dst="usr/share/doc/openubmc/${pkg.name}/docs")
        self.copy("*.MD", dst="usr/share/doc/openubmc/${pkg.name}/docs")
        if self.settings.build_type in ("Dt", ) and os.getenv('TRANSTOBIN') is None:
            return
        os.chdir(self.package_folder)
        for root, dirs, files in os.walk("."):
            for file in files:
                if not file.endswith(".lua") or os.path.islink(file):
                    continue
                file_path = os.path.join(root, file)
                self.run(f"{os.path.expanduser('~')}/.conan/bin/luac -o {file_path} {file_path}")
                self.run(f"{os.path.expanduser('~')}/.conan/bin/luac -s {file_path}")

    def package_info(self):
        if self.settings.arch == "armv8" or self.settings.arch == "x86_64":
            self.cpp_info.libdirs = ["usr/lib64"]
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "usr/lib64"))
        else:
            self.cpp_info.libdirs = ["usr/lib"]
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "usr/lib"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "opt/bmc/apps/${pkg.name}"))
    % if pkg.package_info is not None:
        % if len(pkg.package_info.get("libs", [])) > 0:
        self.cpp_info.libs = [${", ".join("\"" + i + "\"" for i in pkg.package_info["libs"])}]
        % endif
    % endif
    % if "application" in pkg.package_type and pkg.package_info is not None:
        % if len(pkg.package_info.get("bindirs", [])) > 0:
        self.cpp_info.bindirs = [${", ".join("\"" + i + "\"" for i in pkg.package_info["bindirs"])}]
            % for dir in pkg.package_info["bindirs"]:
        self.env_info.PATH.append(os.path.join(self.package_folder, "${dir}"))
            % endfor
        % endif
    % endif
