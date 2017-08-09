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

        conan_file = self.conanfile
        jam_include_paths = ' '.join('"' + path + '"' for path in conan_file.deps_cpp_info.includedirs).replace('\\','/')
        boost_build = conan_file.deps_cpp_info["Boost.Build"]
        boost_build_root_path = boost_build.rootpath
        boost_build_kernel_path = os.path.join(boost_build_root_path, "share/boost-build/src/kernel").replace('\\','/')
        boost_build_jam_content = 'boost-build "' + boost_build_kernel_path + '" ;'
        
        boost_generator = conan_file.deps_cpp_info["Boost.Generator"]
        boost_generator_root_path = boost_generator.rootpath
        boost_generator_source_path = os.path.join(boost_generator_root_path, os.pardir, os.pardir, "source")
        
        template_file_path = os.path.join(boost_generator_source_path, "jamroot.template")
        boostcpp_file_path = os.path.join(boost_generator_source_path, "boostcpp.jam")
        
        template_content = load(template_file_path)
        boostcpp_content = load(boostcpp_file_path)

        deps_info = []
        for dep_name, dep_cpp_info in self.deps_build_info.dependencies:
            deps_libdir = os.path.join(dep_cpp_info.rootpath, dep_cpp_info.libdirs[0])
            if os.path.isfile(os.path.join(deps_libdir,"jamroot.jam")):
                deps_info.append(
                    "use-project /" + dep_name +
                    " : " + deps_libdir.replace('\\','/') + " ;")
        deps_info = "\n".join(deps_info)

        if hasattr(conan_file, 'lib_short_name'):
            libraries = conan_file.lib_short_name
        else:
            libraries = " ".join(conan_file.lib_short_names)

        jamroot_content = template_content \
            .replace("{{{libraries}}}", libraries) \
            .replace("{{{boost_version}}}", conan_file.version) \
            .replace("{{{deps.include_paths}}}", jam_include_paths) \
            .replace("{{{os}}}", self.b2_os()) \
            .replace("{{{address_model}}}", self.b2_address_model()) \
            .replace("{{{architecture}}}", self.b2_architecture()) \
            .replace("{{{deps_info}}}", deps_info) \
            .replace("{{{variant}}}", self.b2_variant()) \
            .replace("{{{name}}}", conan_file.name)
            
        return {
            "boostcpp.jam" : boostcpp_content, 
            "jamroot" : jamroot_content,
            "boost-build.jam" : boost_build_jam_content
        }

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
