from spack import *

from contextlib import closing
from glob import glob
import sys


class Gcc(Package):
    """The GNU Compiler Collection includes front ends for C, C++,
       Objective-C, Fortran, and Java."""
    homepage = "https://gcc.gnu.org"

    url = "http://open-source-box.org/gcc/gcc-4.9.2/gcc-4.9.2.tar.bz2"
    list_url = 'http://open-source-box.org/gcc/'
    list_depth = 2

    version('6.1.0', '8fb6cb98b8459f5863328380fbf06bd1')
    version('5.3.0', 'c9616fd448f980259c31de613e575719')
    version('5.2.0', 'a51bcfeb3da7dd4c623e27207ed43467')
    version('4.9.3', '6f831b4d251872736e8e9cc09746f327')
    version('4.9.2', '4df8ee253b7f3863ad0b86359cd39c43')
    version('4.9.1', 'fddf71348546af523353bd43d34919c1')
    version('4.8.5', '80d2c2982a3392bb0b89673ff136e223')
    version('4.8.4', '5a84a30839b2aca22a2d723de2a626ec')
    version('4.7.4', '4c696da46297de6ae77a82797d2abe28')
    version('4.6.4', 'b407a3d1480c11667f293bfb1f17d1a4')
    version('4.5.4', '27e459c2566b8209ab064570e1b378f7')

    variant('binutils',
            default=sys.platform != 'darwin',
            description="Build via binutils")
    variant('gold',
            default=sys.platform != 'darwin',
            description="Build the gold linker plugin for ld-based LTO")

    depends_on("mpfr")
    depends_on("gmp")
    depends_on("mpc", when='@4.5:')
    depends_on("isl", when='@5.0:')
    depends_on("binutils~libiberty", when='+binutils ~gold')
    depends_on("binutils~libiberty+gold", when='+binutils +gold')

    # TODO: integrate these libraries.
    # depends_on("ppl")
    # depends_on("cloog")
    if sys.platform == 'darwin':
        patch('darwin/gcc-4.9.patch1', when='@4.9.3')
        patch('darwin/gcc-4.9.patch2', when='@4.9.3')
    else:
        provides('golang', when='@4.7.1:')

    def install(self, spec, prefix):
        # libjava/configure needs a minor fix to install into spack paths.
        filter_file(r"'@.*@'", "'@[[:alnum:]]*@'", 'libjava/configure',
                    string=True)

        enabled_languages = set(('c', 'c++', 'fortran', 'java', 'objc'))

        if spec.satisfies("@4.7.1:") and sys.platform != 'darwin':
            enabled_languages.add('go')

        # Generic options to compile GCC
	if spec.satisfies("@4.5:"):
	        options = ["--prefix=%s" % prefix, "--libdir=%s/lib64" % prefix,
                   "--disable-multilib",
                   "--enable-languages=" + ','.join(enabled_languages),
                   "--with-mpc=%s" % spec['mpc'].prefix, "--with-mpfr=%s" %
                   spec['mpfr'].prefix, "--with-gmp=%s" % spec['gmp'].prefix,
                   "--enable-lto", "--with-quad"]
	else:
	        options = ["--prefix=%s" % prefix, "--libdir=%s/lib64" % prefix,
                   "--disable-multilib",
                   "--enable-languages=" + ','.join(enabled_languages),
                   "--with-mpfr=%s" %spec['mpfr'].prefix, 
                   "--with-gmp=%s" % spec['gmp'].prefix,
                   "--enable-lto", "--with-quad"]

        # Binutils
        if spec.satisfies('+binutils'):
            static_bootstrap_flags = "-static-libstdc++ -static-libgcc"
            binutils_options = [
                "--with-sysroot=/", "--with-stage1-ldflags=%s %s" %
                (self.rpath_args, static_bootstrap_flags),
                "--with-boot-ldflags=%s %s" %
                (self.rpath_args, static_bootstrap_flags), "--with-gnu-ld",
                "--with-ld=%s/bin/ld" % spec['binutils'].prefix,
                "--with-gnu-as",
                "--with-as=%s/bin/as" % spec['binutils'].prefix
            ]
            options.extend(binutils_options)
        # Isl
        if 'isl' in spec:
            isl_options = ["--with-isl=%s" % spec['isl'].prefix]
            options.extend(isl_options)

        if sys.platform == 'darwin':
            darwin_options = ["--with-build-config=bootstrap-debug"]
            options.extend(darwin_options)

        build_dir = join_path(self.stage.path, 'spack-build')
        configure = Executable(join_path(self.stage.source_path, 'configure'))
        with working_dir(build_dir, create=True):
            # Rest of install is straightforward.
            configure(*options)
            if sys.platform == 'darwin':
                make("bootstrap")
            else:
                make()
            make("install")

        self.write_rpath_specs()

    @property
    def spec_dir(self):
        # e.g. lib64/gcc/x86_64-unknown-linux-gnu/4.9.2
        spec_dir = glob("%s/lib64/gcc/*/*" % self.prefix)
        return spec_dir[0] if spec_dir else None

    def write_rpath_specs(self):
        """Generate a spec file so the linker adds a rpath to the libs
           the compiler used to build the executable."""
        if not self.spec_dir:
            tty.warn("Could not install specs for %s." %
                     self.spec.format('$_$@'))
            return

        gcc = Executable(join_path(self.prefix.bin, 'gcc'))
        lines = gcc('-dumpspecs', output=str).strip().split("\n")
        specs_file = join_path(self.spec_dir, 'specs')
        with closing(open(specs_file, 'w')) as out:
            for line in lines:
                out.write(line + "\n")
                if line.startswith("*link:"):
                    out.write("-rpath %s/lib:%s/lib64 \\\n" %
                              (self.prefix, self.prefix))
        set_install_permissions(specs_file)
