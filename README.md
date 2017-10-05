## A Conan.io Generator for the Boost C++ Libraries.

[Conan.io](https://conan.io) package for [Boost Libraries](http://www.boost.org/doc/libs/1_65_1/libs/libraries.htm).

The packages generated with this **conanfile** can be found in [Bintray](https://bintray.com/bincrafters/public-conan/Boost.Generator%3Abincrafters).

## To use this package

This package is not intended to be used outside of building the Boost libraries for Conan.io. It is also a special Conan package, in that it is a "**Generator**" package.  [Read about creating custom generators for Conan.io here](conanio.readthedocs.io/en/latest/howtos/dyn_generators.html).  

Generators are distributed just like other packages, and used in other packages as `build_requires`.  Notably, this generator is intended to be used specifically with the boost build system as packaged by Bincrafters.  Below is a summary of how the generation and build process work for this generator; we'll use **Boost.System** as an example. 

### To build and package Boost.System
* Look at the recipe for **Boost.System** here: [Boost System Recipe](https://github.com/bincrafters/conan-boost-system)
* The **Boost.System** library recipe is invoked using `conan create bincrafters/stable`
* This **Boost.Generator** package is listed in `build_requires`, and thus downloaded
* The appropriate version of Boost.Build is also downloaded transitively
* All runtime dependencies listed in `requires` are downloaded
* This generator's `content` method is invoked, producing the file `jamroot` in a conan build directory
* Notably, boostcpp.jam is extracted into a conan directory, which is referenced by the build
* The `build()` step of **Boost.System** is run
  * This calls the Boost Build binary ("**b2**") from a conan directory
  * The generated file `jamroot` is passesd as an argument
* The package step is run, collecting any generated binaries and header files
* The package for **Boost.System** is stored in the local conan cache

### When **Boost.System** is used as dependency
* The **Boost.System** recipe is downloaded from conan
* If the appropriate pre-built binaries are available from the remote repository, they are downloaded
* If not, the build and package process above is executed, and stored in the local conan cache


### Project setup

The following should exist in `conanfile.py` for any Boost library which is not a header-only library, and needs to be built. 

```
	build_requires = "Boost.Generator/1.65.1@bincrafters/stable"
    generators = "boost"
```
	
## For Packagers: Publish this Package

The example below shows the commands used to publish to bincrafters conan repository. To publish to your own conan respository (for example, after forking this git repository), you will need to change the commands below accordingly. 

## Build  and package 

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from `build_requires` and `requires` , and then running the `build()` and `package()` methods. 

    $ conan create bincrafters/stable
	
## Add bincrafters repository to your "remotes"

	$ conan remote add bincrafters "https://api.bintray.com/conan/bincrafters/public-conan"

## Upload to bintray 

    $ conan upload --all --remote bincrafters Boost.Generator/1.65.1@bincrafters/stable

### License
[Boost](www.boost.org/LICENSE_1_0.txt)
