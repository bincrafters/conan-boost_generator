from conans.model.conan_generator import Generator
from conans import ConanFile, os, tools, load

# This is the normal packaging info since generators
# get published just like other packages. Although
# most of the standard package methods are overridden
# when there is another class derived from "generator" present.


class BoostGenerator(ConanFile):
    name = "Boost.Generator"
    version = "0.0.1"
    url = "https://github.com/bincrafters/conan-boost-generator"
    description = "Conan build generator for boost libraries http://www.boost.org/doc/libs/1_64_0/libs/libraries.htm"
    license = "BSL"
    boost_version = "1.64.0"
    exports = "boostcpp.jam", "jamroot.template"
    requires = "Boost.Build/1.64.0@bincrafters/testing"
    
       
# Below is the actual generator code


class boost(Generator):
   
    @property
    def filename(self):
        pass #in this case, filename defined in return value of content method

    @property
    def content(self):
        jam_include_paths = ' '.join('"' + path + '"' for path in self.conanfile.deps_cpp_info.includedirs).replace('\\','/')
     
        libraries_to_build = " ".join(self.conanfile.lib_short_names)

        jamroot_content = self.get_template_content() \
            .replace("{{{libraries}}}", libraries_to_build) \
            .replace("{{{boost_version}}}", self.conanfile.version) \
            .replace("{{{deps.include_paths}}}", jam_include_paths) \
            .replace("{{{os}}}", self.b2_os()) \
            .replace("{{{address_model}}}", self.b2_address_model()) \
            .replace("{{{architecture}}}", self.b2_architecture()) \
            .replace("{{{deps_info}}}", self.get_deps_info_for_jamfile()) \
            .replace("{{{variant}}}", self.b2_variant()) \
            .replace("{{{name}}}", self.conanfile.name)
            
           
        return {
            "jamroot" : jamroot_content,
            "boostcpp.jam" : self.get_boostcpp_content(), 
            "boost-build.jam" : self.get_boost_build_jam_content(),
            "project-config.jam" : ""
        }

    def get_boost_build_jam_content(self):
        boost_build = self.conanfile.deps_cpp_info["Boost.Build"]
        boost_build_root_path = boost_build.rootpath
        boost_build_kernel_path = os.path.join(boost_build_root_path, "share/boost-build/src/kernel").replace('\\','/')
        boost_build_jam_content = 'boost-build "' + boost_build_kernel_path + '" ;'
        return boost_build_jam_content

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

    def b2_architecture(self):
        if str(self.settings.arch).startswith('x86'):
            return 'x86'
        elif str(self.settings.arch).startswith('ppc'):
            return 'power'
        elif str(self.settings.arch).startswith('arm'):
            return 'arm'
        else:
            return ""
    
    def b2_variant(self):
        if str(self.settings.build_type) == "Debug":
            return "debug"
        else:
            return "release"
