##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
import spack
from spack import *
import llnl.util.tty as tty

class Binutils(Package):
    """GNU binutils, which contain the linker, assembler, objdump and others"""
    homepage = "http://www.gnu.org/software/binutils/"

    url="https://ftp.gnu.org/gnu/binutils/binutils-2.25.tar.bz2"

    version('2.26', '64146a0faa3b411ba774f47d41de239f')
    version('2.25', 'd9f3303f802a5b6b0bb73a335ab89d66')
    version('2.24', 'e0f71a7b2ddab0f8612336ac81d9636b')
    version('2.23.2', '4f8fa651e35ef262edc01d60fb45702e')
    version('2.20.1', '2b9dc8f2b7dbd5ec5992c6e29de0b764')

    depends_on('m4')
    depends_on('flex')
    depends_on('bison')

    # Add a patch that creates binutils libiberty_pic.a which is preferred by OpenSpeedShop and cbtf-krell
    variant('krellpatch', default=False, description="build with openspeedshop based patch.")
    variant('gold', default=True, description="build the gold linker")
    patch('binutilskrell-2.24.patch', when='@2.24+krellpatch')

    patch('cr16.patch')

    variant('libiberty', default=False, description='Also install libiberty.')

    curl_options=[
        '-k']

    def do_fetch(self, mirror_only=False):
        # Add our custom curl commandline options
        tty.msg(
            "[Binutils] Adding required commandline options to curl " +
            "before performing fetch: %s" %
            (self.curl_options))

        for option in self.curl_options:
            spack.curl.add_default_arg(option)

        # Now perform the actual fetch
        super(Binutils, self).do_fetch(mirror_only)


    def install(self, spec, prefix):
        configure_args = [
            '--prefix=%s' % prefix,
            '--disable-dependency-tracking',
            '--disable-werror',
            '--enable-interwork',
            '--enable-multilib',
            '--enable-shared',
            '--enable-64-bit-bfd',
            '--enable-targets=all',
            '--with-sysroot=/']

        if '+gold' in spec:
            configure_args.append('--enable-gold')

        if '+libiberty' in spec:
            configure_args.append('--enable-install-libiberty')

        configure(*configure_args)
        make()
        make("install")
