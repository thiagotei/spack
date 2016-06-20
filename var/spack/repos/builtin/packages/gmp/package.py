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

class Gmp(Package):
    """GMP is a free library for arbitrary precision arithmetic,
       operating on signed integers, rational numbers, and
       floating-point numbers."""
    homepage = "https://gmplib.org"
    url      = "https://gmplib.org/download/gmp/gmp-6.0.0a.tar.bz2"

    version('6.1.0' , '86ee6e54ebfc4a90b643a65e402c4048')
    version('6.0.0a', 'b7ff2d88cae7f8085bd5006096eed470')
    version('6.0.0' , '6ef5869ae735db9995619135bd856b84')

    depends_on("m4")

    curl_options=[
        '-k']

    def do_fetch(self, mirror_only=False):
        # Add our custom curl commandline options
        tty.msg(
            "[Gmp] Adding required commandline options to curl " +
            "before performing fetch: %s" %
            (self.curl_options))

        for option in self.curl_options:
            spack.curl.add_default_arg(option)

        # Now perform the actual fetch
        super(Gmp, self).do_fetch(mirror_only)

    def install(self, spec, prefix):
        configure("--prefix=%s" % prefix)
        make()
        make("install")
