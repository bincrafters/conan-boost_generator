from conans.model.conan_generator import Generator
from conans import ConanFile, os, tools, load

# This is the normal packaging info since generators
# get published just like other packages. Although
# most of the standard package methods are overridden
# when there is another class derived from "generator" present.


class BoostGenerator(ConanFile):
    name = "Boost.Generator"
    version = "1.65.1"
    url = "https://github.com/bincrafters/conan-boost-generator"
    description = "Conan build generator for boost libraries http://www.boost.org/doc/libs/1_65_1/libs/libraries.htm"
    license = "BSL"
    exports = "boostcpp.jam", "jamroot.template", "project-config.template.jam"
    requires = "Boost.Build/1.65.1@bincrafters/stable"

    def package_info(self):
        self.user_info.b2_command = "b2 -j%s -a --hash=yes --debug-configuration"%(tools.cpu_count())

# Below is the actual generator code


class boost(Generator):
   
    @property
    def filename(self):
        pass  # in this case, filename defined in return value of content method

    @property
    def content(self):
        jam_include_paths = ' '.join('"' + path + '"' for path in self.conanfile.deps_cpp_info.includedirs).replace('\\','/')
     
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
            .replace("{{{libcxx}}}", self.b2_libcxx)
            
           
        return {
            "jamroot" : jamroot_content,
            "boostcpp.jam" : self.get_boostcpp_content(), 
            "project-config.jam" : self.get_project_config_content(),
            "short_path.cmd" : "@echo off\nECHO %~s1"
        }

    def get_template_content(self):
        template_file_path = os.path.join(self.get_boost_generator_source_path(), "jamroot.template")
        template_content = load(template_file_path)
        return template_content

    def get_boostcpp_content(self):
        boostcpp_file_path = os.path.join(self.get_boost_generator_source_path(), "boostcpp.jam")
        boostcpp_content = load(boostcpp_file_path)
        return boostcpp_content
        
    def get_boost_generator_source_path(self):
        boost_generator = self.conanfile.deps_cpp_info["Boost.Generator"]
        boost_generator_root_path = boost_generator.rootpath
        boost_generator_source_path = os.path.join(boost_generator_root_path, os.pardir, os.pardir, "export")
        return boost_generator_source_path
        
    def get_deps_info_for_jamfile(self):
        deps_info = []
        for dep_name, dep_cpp_info in self.deps_build_info.dependencies:
            dep_libdir = os.path.join(dep_cpp_info.rootpath, dep_cpp_info.libdirs[0])
            if os.path.isfile(os.path.join(dep_libdir,"jamroot.jam")):
                deps_info.append(
                    "use-project /" + dep_name +  " : " + dep_libdir.replace('\\','/') + " ;")
                try:
                    dep_short_names = self.conanfile.deps_user_info[dep_name].lib_short_names.split(",")
                    for dep_short_name in dep_short_names:
                        deps_info.append(
                            'LIBRARY_DIR(' + dep_short_name + ') = "' + dep_libdir.replace('\\','/') + '" ;')
                except KeyError:
                    pass

        deps_info = "\n".join(deps_info)
        return deps_info

    def get_project_config_content(self):
        project_config_content_file_path = os.path.join(self.get_boost_generator_source_path(), "project-config.template.jam")
        project_config_content = load(project_config_content_file_path)
        return project_config_content \
            .replace("{{{toolset}}}", self.b2_toolset) \
            .replace("{{{toolset_version}}}", self.b2_toolset_version) \
            .replace("{{{toolset_exec}}}", self.b2_toolset_exec) \
            .replace("{{{zlib_lib_paths}}}", self.zlib_lib_paths) \
            .replace("{{{zlib_include_paths}}}", self.zlib_include_paths) \
            .replace("{{{bzip2_lib_paths}}}", self.bzip2_lib_paths) \
            .replace("{{{bzip2_include_paths}}}", self.bzip2_include_paths) \
            .replace("{{{python_exec}}}", self.b2_python_exec) \
            .replace("{{{python_version}}}", self.b2_python_version)

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
        if self.b2_os == 'linux' or self.b2_os == 'freebsd' or self.b2_os == 'solaris' or self.b2_os == 'darwin':
            version = str(self.settings.compiler.version).split('.')
            result_x = self.b2_toolset + "-" + version[0]
            result_xy = result_x + version[1] if version[1] != '0' else ''
            class dev_null(object):
                def write(self, message):
                    pass
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
            return self.win_get_cl_path or "$(DEFAULT)"
        else:
            return "$(DEFAULT)"

    @property
    def win_get_cl_path(self):
        vs_root = tools.vs_installation_path(str(self.settings.compiler.version))
        if vs_root:
            cl_path_1 = os.path.join(vs_root, "VC", "Tools", "MSVC", "*", "bin", "*", "*", "cl.exe")
            if os.path.isfile(cl_path_1):
                return cl_path_1.replace("\\", "/")
            else:
                cl_path_2 = os.path.join(vs_root, "VC", "bin", "cl.exe")
                if os.path.isfile(cl_path_2):
                    return cl_path_2.replace("\\", "/")

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
                return '"{0}"'.format('" "'.join(self.deps_build_info["zlib"].lib_paths))
        except:
            pass
        return ""
    
    @property
    def zlib_include_paths(self):
        try:
            if self.conanfile.options.use_zlib:
                return '"{0}"'.format('" "'.join(self.deps_build_info["zlib"].include_paths))
        except:
            pass
        return ""
    
    @property
    def bzip2_lib_paths(self):
        try:
            if self.conanfile.options.use_zlib:
                return '"{0}"'.format('" "'.join(self.deps_build_info["bzip2"].lib_paths))
        except:
            pass
        return ""
    
    @property
    def bzip2_include_paths(self):
        try:
            if self.conanfile.options.use_bzip2:
                return '"{0}"'.format('" "'.join(self.deps_build_info["bzip2"].include_paths))
        except:
            pass
        return ""
    
    @property
    def b2_libcxx(self):
        if self.b2_toolset == 'gcc':
            if str(self.settings.compiler.libcxx) == 'libstdc++11':
                return '<cflags>-std=c++11 <linkflags>-std=c++11'
        elif self.b2_toolset == 'clang':
            if str(self.settings.compiler.libcxx) == 'libc++':
                return '<cflags>-stdlib=libc++ <linkflags>-stdlib=libc++'
            elif str(self.settings.compiler.libcxx) == 'libstdc++11':
                return '<cflags>-stdlib=libstdc++ <linkflags>-stdlib=libstdc++ <cflags>-std=c++11 <linkflags>-std=c++11'
            else:
                return '<cflags>-stdlib=libstdc++ <linkflags>-stdlib=libstdc++'
        return ''
    
    @property
    def b2_python_exec(self):
        try:
            return '"'+str(self.conanfile.options.python).replace("\\","/")+'"'
        except:
            return ""
    
    @property
    def b2_python_version(self):
        pyexec = self.b2_python_exec
        if pyexec:
            class get_pyver():
                def __init__(self):
                    self.value = ""
                def write(self,m):
                    self.value = self.value+m.strip()
            pyver = get_pyver()
            self.conanfile.run(
                '''{0} -c "from sys import *; print('%d.%d' % (version_info[0],version_info[1]))"'''.format(pyexec),
                output=pyver)
            return pyver.value
        else:
            return ""
