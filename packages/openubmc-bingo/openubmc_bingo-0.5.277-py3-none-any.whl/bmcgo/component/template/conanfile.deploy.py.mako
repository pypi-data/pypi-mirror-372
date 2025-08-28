from conans import ConanFile, CMake
import yaml
import os


class DeployConan(ConanFile):
    name = "${pkg.name}-deploy"
    version = "0.0.1"
    settings = "os", "compiler", "build_type", "arch"
    license = "Mulan PSL v2"
    generators = "cmake"
    requires = []

    def export(self):
        self.copy("manifest.yaml")

    def requirements(self):
        uc = ""
        if self.user and self.channel:
            if self.channel == "dev":
                uc = f"@{self.user}/rc"
            else:
                uc = f"@{self.user}/{self.channel}"

        % for build_dep in dependencies:
            % if "@" in build_dep:
        self.requires("${build_dep}")
            % else:
        self.requires(f"${build_dep}{uc}")
            % endif
        % endfor

    def build(self):
        pass

    def package(self):
        pass

    def package_info(self):
        pass
