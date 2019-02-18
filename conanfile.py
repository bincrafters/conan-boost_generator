#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans.model.conan_generator import Generator
from conans import ConanFile, tools, load
import glob
import locale
import subprocess
import os
import sys

# This is the normal packaging info since generators
# get published just like other packages. Although
# most of the standard package methods are overridden
# when there is another class derived from "generator" present.


class BoostGenerator(ConanFile):
    name = "boost_generator"
    version = "1.69.0"
    url = "https://github.com/bincrafters/conan-boost_generator"
    description = "Conan build generator for boost libraries http://www.boost.org/doc/libs/1_69_0/libs/libraries.htm"
    license = "BSL"
    exports = "boostcpp.jam", "jamroot.template", "project-config.template.jam"
    requires = "boost_build/1.69.0@bincrafters/stable"

# Below is the actual generator code


class boost(Generator):

    @property
    def filename(self):
        pass  # in this case, filename defined in return value of content method

    @property
    def content(self):
        # print("@@@@@@@@ BoostGenerator:boost.content: " + str(self.conanfile))
        try:
            jam_include_paths = ' '.join('"' + path + '"' for path in self.conanfile.deps_cpp_info.includedirs).replace('\\', '/')

            libraries_to_build = " ".join(self.conanfile.lib_short_names)

            jamroot_content = self.get_template_content() \
                .replace("{{{toolset}}}", self.b2_toolset) \
                .replace("{{{libraries}}}", libraries_to_build) \
                .replace("{{{boost_version}}}", self.conanfile.version) \
                .replace("{{{deps.include_paths}}}", jam_include_paths) \
                .replace("{{{os}}}", self.b2_os) \
                .replace("{{{address_model}}}", self.b2_address_model) \
                .replace("{{{architecture}}}", self.b2_architecture) \
                .replace("{{{deps_info}}}", self.get_deps_info_for_jamfile()) \
                .replace("{{{variant}}}", self.b2_variant) \
                .replace("{{{name}}}", self.conanfile.name) \
                .replace("{{{link}}}", self.b2_link) \
                .replace("{{{runtime_link}}}", self.b2_runtime_link) \
                .replace("{{{toolset_version}}}", self.b2_toolset_version) \
                .replace("{{{toolset_exec}}}", self.b2_toolset_exec) \
                .replace("{{{libcxx}}}", self.b2_libcxx) \
                .replace("{{{cxxstd}}}", self.b2_cxxstd) \
                .replace("{{{cxxabi}}}", self.b2_cxxabi) \
                .replace("{{{libpath}}}", self.b2_icu_lib_paths) \
                .replace("{{{arch_flags}}}", self.b2_arch_flags) \
                .replace("{{{isysroot}}}", self.b2_isysroot) \
                .replace("{{{fpic}}}", self.b2_fpic) \
                .replace("{{{threading}}}", self.b2_threading) \
                .replace("{{{threadapi}}}", self.b2_threadapi) \
                .replace("{{{profile_flags}}}", self.b2_profile_flags)

            return {
                "jamroot" : jamroot_content,
                "boostcpp.jam" : self.get_boostcpp_content(),
                "project-config.jam" : self.get_project_config_content(),
                "short_path.cmd" : "@echo off\nECHO %~s1"
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

    def get_template_content(self):
        template_file_path = os.path.join(self.get_boost_generator_source_path(), "jamroot.template")
        template_content = load(template_file_path)
        return template_content

    def get_boostcpp_content(self):
        boostcpp_file_path = os.path.join(self.get_boost_generator_source_path(), "boostcpp.jam")
        boostcpp_content = load(boostcpp_file_path)
        return boostcpp_content

    def get_boost_generator_source_path(self):
        boost_generator = self.conanfile.deps_cpp_info["boost_generator"]
        boost_generator_root_path = boost_generator.rootpath
        boost_generator_source_path = os.path.join(boost_generator_root_path, os.pardir, os.pardir, "export")
        return boost_generator_source_path

    def get_deps_info_for_jamfile(self):
        deps_info = []
        for dep_name, dep_cpp_info in self.deps_build_info.dependencies:
            for libdir in dep_cpp_info.libdirs:
                dep_libdir = os.path.join(dep_cpp_info.rootpath, libdir)
                if os.path.isfile(os.path.join(dep_libdir, "jamroot.jam")):
                    lib_short_name = os.path.basename(os.path.dirname(dep_libdir))
                    lib_project_name = "\"/" + dep_name + "," + lib_short_name + "\""
                    deps_info.append(
                        "use-project " + lib_project_name + " : \"" + dep_libdir.replace('\\', '/') + "\" ;")
                    deps_info.append(
                        "alias \"" + lib_short_name + "\" : " + lib_project_name + " ;")
                    try:
                        dep_short_names = self.conanfile.deps_user_info[dep_name].lib_short_names.split(",")
                        for dep_short_name in dep_short_names:
                            deps_info.append(
                                '"LIBRARY_DIR(' + dep_short_name + ')" = "' + dep_libdir.replace('\\', '/') + '" ;')
                    except KeyError:
                        pass

        deps_info = "\n".join(deps_info)
        return deps_info

    def get_project_config_content(self):
        project_config_content_file_path = os.path.join(self.get_boost_generator_source_path(),
                                                        "project-config.template.jam")
        project_config_content = load(project_config_content_file_path)
        return project_config_content \
            .replace("{{{toolset}}}", self.b2_toolset) \
            .replace("{{{toolset_version}}}", self.b2_toolset_version) \
            .replace("{{{toolset_exec}}}", self.b2_toolset_exec) \
            .replace("{{{zlib_lib_paths}}}", self.zlib_lib_paths) \
            .replace("{{{zlib_include_paths}}}", self.zlib_include_paths) \
            .replace("{{{zlib_name}}}", self.zlib_lib_name) \
            .replace("{{{bzip2_lib_paths}}}", self.bzip2_lib_paths) \
            .replace("{{{bzip2_include_paths}}}", self.bzip2_include_paths) \
            .replace("{{{bzip2_name}}}", self.bzip2_lib_name) \
            .replace("{{{lzma_lib_paths}}}", self.lzma_lib_paths) \
            .replace("{{{lzma_include_paths}}}", self.lzma_include_paths) \
            .replace("{{{lzma_name}}}", self.lzma_lib_name) \
            .replace("{{{zstd_lib_paths}}}", self.zstd_lib_paths) \
            .replace("{{{zstd_include_paths}}}", self.zstd_include_paths) \
            .replace("{{{zstd_name}}}", self.zstd_lib_name) \
            .replace("{{{python_exec}}}", self.b2_python_exec) \
            .replace("{{{python_version}}}", self.b2_python_version) \
            .replace("{{{python_include}}}", self.b2_python_include) \
            .replace("{{{python_lib}}}", self.b2_python_lib) \
            .replace("{{{mpicxx}}}", self.b2_mpicxx) \
            .replace("{{{profile_tools}}}", self.b2_profile_tools)

    @property
    def b2_os(self):
        b2_os = {
            'Windows': 'windows',
            'Linux': 'linux',
            'Macos': 'darwin',
            'Android': 'android',
            'iOS': 'iphone',
            'FreeBSD': 'freebsd',
            'SunOS': 'solaris'}
        return b2_os[str(self.settings.os)]

    @property
    def b2_address_model(self):
        b2_address_model = {
            'x86': '32',
            'x86_64': '64',
            'ppc64le': '64',
            'ppc64': '64',
            'armv6': '32',
            'armv7': '32',
            'armv7hf': '32',
            'armv8': '64'}
        return b2_address_model[str(self.settings.arch)]

    @property
    def b2_architecture(self):
        if str(self.settings.arch).startswith('x86'):
            return 'x86'
        elif str(self.settings.arch).startswith('ppc'):
            return 'power'
        elif str(self.settings.arch).startswith('arm'):
            return 'arm'
        else:
            return ""

    @property
    def b2_variant(self):
        if str(self.settings.build_type) == "Debug":
            return "debug"
        else:
            return "release"

    @property
    def b2_toolset(self):
        b2_toolsets = {
            'gcc': 'gcc',
            'Visual Studio': 'msvc',
            'clang': 'clang',
            'apple-clang': 'clang'}
        return b2_toolsets[str(self.settings.compiler)]

    @property
    def b2_toolset_version(self):
        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version == "15":
                return "14.1"
            else:
                return str(self.settings.compiler.version) + ".0"
        else:
            return "$(DEFAULT)"

    @property
    def b2_toolset_exec(self):
        if self.b2_os in ['linux', 'freebsd', 'solaris', 'darwin', 'android'] or \
                (self.b2_os == 'windows' and self.b2_toolset == 'gcc'):

            class dev_null(object):

                def write(self, message):
                    pass

            if 'CXX' in os.environ:
                try:
                    self.conanfile.run(os.environ['CXX'] + ' --version', output=dev_null())
                    return os.environ['CXX']
                except:
                    pass
            version = str(self.settings.compiler.version).split('.')
            result_x = self.b2_toolset.replace('gcc', 'g++') + "-" + version[0]
            result_xy = result_x
            if len(version) > 1:
                result_xy += version[1] if version[1] != '0' else ''

            try:
                self.conanfile.run(result_xy + " --version", output=dev_null())
                return result_xy
            except:
                pass
            try:
                self.conanfile.run(result_x + " --version", output=dev_null())
                return result_x
            except:
                pass
            return "$(DEFAULT)"
        elif self.b2_os == "windows":
            return self.win_cl_exe or "$(DEFAULT)"
        else:
            return "$(DEFAULT)"

    @property
    def win_cl_exe(self):
        vs_root = tools.vs_installation_path(str(self.settings.compiler.version))
        if vs_root:
            cl_exe = \
                glob.glob(os.path.join(vs_root, "VC", "Tools", "MSVC", "*", "bin", "*", "*", "cl.exe")) + \
                glob.glob(os.path.join(vs_root, "VC", "bin", "cl.exe"))
            if cl_exe:
                return cl_exe[0].replace("\\", "/")

    @property
    def b2_link(self):
        shared = False
        try:
            shared = self.conanfile.options.shared
        except:
            pass
        return "shared" if shared else "static"

    @property
    def b2_runtime_link(self):
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime:
            return "static" if "MT" in str(self.settings.compiler.runtime) else "$(DEFAULT)"
        return "$(DEFAULT)"

    @property
    def zlib_lib_paths(self):
        try:
            if self.conanfile.options.use_zlib:
                return '"{0}"'.format('" "'.join(self.deps_build_info["zlib"].lib_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def zlib_include_paths(self):
        try:
            if self.conanfile.options.use_zlib:
                return '"{0}"'.format('" "'.join(self.deps_build_info["zlib"].include_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def zlib_lib_name(self):
        try:
            if self.conanfile.options.use_zlib:
                return os.path.basename(self.deps_build_info["zlib"].libs[0])
        except:
            pass
        return ""

    @property
    def bzip2_lib_paths(self):
        try:
            if self.conanfile.options.use_bzip2:
                return '"{0}"'.format('" "'.join(self.deps_build_info["bzip2"].lib_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def bzip2_include_paths(self):
        try:
            if self.conanfile.options.use_bzip2:
                return '"{0}"'.format('" "'.join(self.deps_build_info["bzip2"].include_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def bzip2_lib_name(self):
        try:
            if self.conanfile.options.use_bzip2:
                return os.path.basename(self.deps_build_info["bzip2"].libs[0])
        except:
            pass
        return ""

    @property
    def lzma_lib_paths(self):
        try:
            if self.conanfile.options.use_lzma:
                return '"{0}"'.format('" "'.join(self.deps_build_info["lzma"].lib_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def lzma_include_paths(self):
        try:
            if self.conanfile.options.use_lzma:
                return '"{0}"'.format('" "'.join(self.deps_build_info["lzma"].include_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def lzma_lib_name(self):
        try:
            if self.conanfile.options.use_lzma:
                return os.path.basename(self.deps_build_info["lzma"].libs[0])
        except:
            pass
        return ""

    @property
    def zstd_lib_paths(self):
        try:
            if self.conanfile.options.use_zstd:
                return '"{0}"'.format('" "'.join(self.deps_build_info["zstd"].lib_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def zstd_include_paths(self):
        try:
            if self.conanfile.options.use_zstd:
                return '"{0}"'.format('" "'.join(self.deps_build_info["zstd"].include_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def zstd_lib_name(self):
        try:
            if self.conanfile.options.use_zstd:
                return os.path.basename(self.deps_build_info["zstd"].libs[0])
        except:
            pass
        return ""

    @property
    def b2_cxxstd(self):
        # for now, we use C++11 as default, unless we're targeting libstdc++ (not 11)
        if self.b2_toolset in ['gcc', 'clang'] and self.b2_os != 'android':
            if str(self.settings.compiler.libcxx) != 'libstdc++':
                return '<cxxflags>-std=c++11 <linkflags>-std=c++11'
        return ''

    @property
    def b2_cxxabi(self):
        if self.b2_toolset in ['gcc', 'clang'] and self.b2_os != 'android':
            if str(self.settings.compiler.libcxx) == 'libstdc++11':
                return '<define>_GLIBCXX_USE_CXX11_ABI=1'
            elif str(self.settings.compiler.libcxx) == 'libstdc++':
                return '<define>_GLIBCXX_USE_CXX11_ABI=0'
        return ''

    @property
    def b2_libcxx(self):
        if self.b2_toolset == 'clang' and self.b2_os != 'android':
            if str(self.settings.compiler.libcxx) == 'libc++':
                return '<cxxflags>-stdlib=libc++ <linkflags>-stdlib=libc++'
            elif str(self.settings.compiler.libcxx) in ['libstdc++11', 'libstdc++']:
                return '<cxxflags>-stdlib=libstdc++ <linkflags>-stdlib=libstdc++'
        return ''

    _python_dep = "python_dev_config"

    @property
    def b2_python_exec(self):
        try:
            return self.conanfile.deps_user_info[self._python_dep].python_exec.replace('\\', '/')
        except:
            return ""

    @property
    def b2_python_version(self):
        try:
            return self.conanfile.deps_user_info[self._python_dep].python_version.replace('\\', '/')
        except:
            return ""

    @property
    def b2_python_include(self):
        try:
            return self.conanfile.deps_user_info[self._python_dep].python_include_dir.replace('\\', '/')
        except:
            return ""

    @property
    def b2_python_lib(self):
        try:
            if self.settings.compiler == "Visual Studio":
                return self.conanfile.deps_user_info[self._python_dep].python_lib_dir.replace('\\', '/')
            else:
                return self.conanfile.deps_user_info[self._python_dep].python_lib.replace('\\', '/')
        except:
            return ""

    @property
    def b2_icu_lib_paths(self):
        try:
            if self.conanfile.options.use_icu:
                return '"{0}"'.format('" "'.join(self.deps_build_info["icu"].lib_paths)).replace('\\', '/')
        except:
            pass
        return ""

    @property
    def apple_arch(self):
        if self.settings.arch == "armv7":
            return "armv7"
        elif self.settings.arch == "armv8":
            return "arm64"
        elif self.settings.arch == "x86":
            return "i386"
        elif self.settings.arch == "x86_64":
            return "x86_64"
        else:
            return None

    @property
    def apple_sdk(self):
        if self.settings.os == "Macos":
            return "macosx"
        elif self.settings.os == "iOS":
            if str(self.settings.arch).startswith('x86'):
                return "iphonesimulator"
            elif str(self.settings.arch).startswith('arm'):
                return "iphoneos"
            else:
                return None
        return None

    def command_output(self, command):
        if sys.version_info.major >= 3:
            return subprocess.check_output(command, shell=False, encoding=locale.getpreferredencoding()).strip()
        else:
            return subprocess.check_output(command, shell=False).strip()

    @property
    def apply_isysroot(self):
        return self.command_output(['xcrun', '--show-sdk-path', '-sdk', self.apple_sdk])

    @property
    def b2_arch_flags(self):
        if self.b2_os == 'darwin' or self.b2_os == 'iphone':
            return '<flags>"-arch {0}" <linkflags>"-arch {0}"'.format(self.apple_arch)
        return ''

    @property
    def b2_isysroot(self):
        if self.b2_os == 'darwin' or self.b2_os == 'iphone':
            return '<flags>"-isysroot {0}"'.format(self.apply_isysroot)
        return ''

    @property
    def b2_fpic(self):
        if self.b2_os != 'windows' and self.b2_toolset in ['gcc', 'clang'] and self.b2_link == 'static':
            return '<flags>-fPIC\n<cxxflags>-fPIC'
        return ''

    @property
    def b2_mpicxx(self):
        try:
            return str(self.conanfile.options.mpicxx)
        except:
            return ''

    @property
    def b2_threading(self):
        return 'multi'

    @property
    def b2_threadapi(self):
        try:
            result = str(self.conanfile.options.threadapi)
            if result != 'default':
                return result
        except:
            pass
        try:
            if str(self.settings.threads) == 'posix':
                return 'pthread'
            if str(self.settings.threads) == 'win32':
                return 'win32'
        except:
            pass
        if self.b2_os == 'windows':
            return 'win32'
        else:
            return 'pthread'

    @property
    def b2_profile_flags(self):
        def format_b2_flags(token, flags):
            return '%s"%s"' % (token, flags)

        if self.b2_toolset == 'gcc' or self.b2_toolset == 'clang':
            additional_flags = []
            if 'CFLAGS' in os.environ:
                additional_flags.append(format_b2_flags('<cflags>', os.environ['CFLAGS']))
            if 'CXXFLAGS' in os.environ:
                additional_flags.append(format_b2_flags('<cxxflags>', os.environ['CXXFLAGS']))
            if 'LDFLAGS' in os.environ:
                additional_flags.append(format_b2_flags('<linkflags>', os.environ['LDFLAGS']))
            return '\n'.join(additional_flags)
        else:
            return ''

    @property
    def b2_profile_tools(self):
        if self.b2_toolset == 'gcc' or self.b2_toolset == 'clang':
            additional_flags = []
            if 'SYSROOT' in os.environ:
                additional_flags.append('<root>"%s"' % os.environ['SYSROOT'])
            if 'AR' in os.environ:
                additional_flags.append('<archiver>"%s"' % os.environ['AR'])
            if 'RANLIB' in os.environ:
                additional_flags.append('<ranlib>"%s"' % os.environ['RANLIB'])
            if self.b2_os == 'darwin' or self.b2_os == 'iphone':
                if 'STRIP' in os.environ:
                    additional_flags.append('<striper>"%s"' % os.environ['STRIP'])
            additional_flags = ' '.join(additional_flags)
            if len(additional_flags):
                additional_flags = ': ' + additional_flags
            return additional_flags
        else:
            return ''
