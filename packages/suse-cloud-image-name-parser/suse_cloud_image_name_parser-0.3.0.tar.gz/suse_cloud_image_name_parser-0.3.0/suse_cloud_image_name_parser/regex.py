# Copyright (c) 2025 SUSE LLC
#
# This file is part of suse-cloud-image-name-parser
#
# image-name is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or # (at your option) any later version.
#
# image-name is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with image-name.
# If not, see <http://www.gnu.org/licenses/>.

import logging
import re

_logger = logging.getLogger(__name__)


class SUSECloudImageNameRegexp:
    """Manages the construction of a Regular Expression that can be used to
    match valid pint image names, and extract the relevant content from
    them as named fields in the returned match object's ``groupdict()``.
    """

    uuid_prefix = r'(?:(?P<uuid_prefix>[0-9a-fA-F]*)__)?'
    basename_pre = r'(?P<base_name>'
    basename_post = r')'
    product_pre = r'(?P<product>'
    product_post = r')'
    prodbase_pre = r'(?P<prodbase>'
    prodbase_post = r')'
    suffix_pre = r'(?P<suffix>'
    suffix_post = r')'
    sle_server = r'(?:(?:suse-)?(?P<sle_server>sles))'
    sle = r'(?:(?:suse-)?(?P<sle>sle))'
    opensuse_leap = r'(?:(?:suse-)?(?P<leap>open(suse|SUSE)-[l|L]eap))'
    suse_manager = r'(?P<suse_manager>suse-manager)'
    product_version = (r'(' +
                       r'(?:-?(?P<major_version>[0-9]+))?' +
                       r'(?:[.-](?P<minor_version>(?:[sS][pP][1-9]|[0-9])))?' +
                       r')')
    sapcal = r'(?:-(?P<sapcal>sapcal))?'
    azure_hosted = r'(?:-azure-(?P<azure_hosted>li|vli))?'
    sap1 = r'(?:-(?P<sap1>sap))?'
    sap2 = r'(?:-(?P<sap2>(?(sapcal)|sap)))?'
    basic = r'(?:-(?P<basic>basic))?'
    suma_type = (r'(?(suse_manager)' +
                 r'(?:-(?P<suma_type>proxy|server))' +
                 r'|)')
    byos = r'(?:-(?P<byos>byos))?'
    chost = r'(?:-(?P<chost>chost))?'
    micro = r'(?:-(?P<micro>micro))?'
    hpc1 = r'(?:-(?P<hpc1>hpc))?'
    hpc2 = r'(?:-(?P<hpc2>hpc))?'
    hardened = r'(?:-(?P<hardened>hardened))?'
    datestamp = r'(?:-v(?P<datestamp>[0-9]{8,9}))?'
    ecs = r'(?:-(?P<ecs>ecs))?'
    gen_id = (r'(?:-(?P<gen_id>(?:(?P=major_version)' +
              r'(?:-(?P=minor_version))?-)?gen[0-9]))?')
    virt_type = r'(?:-(?P<virt_type>hvm|pv))?'
    ssd = r'(?:-(?P<ssd>ssd))?'
    arch = r'(?:-(?P<arch>x86_64|x86-64|arm64))?'
    mp_account = r'(?:-(?P<mp_account>ltd|llc))?'

    @classmethod
    def matcher(cls):
        """Helper class method that constructs the required regexp
        pattern and returns the compiled result."""

        # Construct a regexp pattern that matches the base product
        # part of an image name, e.g. sles, suse-manager, opensuse,
        # including any optional 'suse-' prefix that may exist for
        # some cloud providers.
        prodbase_pattern = (cls.prodbase_pre +
                            cls.sle_server +
                            r'|' +
                            cls.sle +
                            r'|' +
                            cls.opensuse_leap +
                            r'|' +
                            cls.suse_manager +
                            r'|' +
                            cls.prodbase_post)

        # Construct a regexp pattern that matches the entire product
        # identification part of the image name, before the product
        # version part, e.g. sles-sap or sles-hpc.
        prod_pattern = (cls.product_pre +
                        prodbase_pattern +
                        cls.hpc1 +
                        cls.sap1 +
                        cls.micro +
                        cls.product_post)

        # Construct a pattern that matches the entire image basename,
        # i.e. the entire part that comes before the '-v{date}', but
        # excluding the Azure '<UUID>__' prefix, made up of the base
        # product, with any product flavour identifiers, followed by
        # the product version, followed by further possible flavour
        # and payment model identifiers.
        basename_pattern = (cls.basename_pre +
                            prod_pattern +
                            cls.suma_type +
                            cls.product_version +
                            cls.basic +
                            cls.sapcal +
                            cls.sap2 +
                            cls.chost +
                            cls.hpc2 +
                            cls.hardened +
                            cls.azure_hosted +
                            cls.byos +
                            cls.basename_post)

        # Construct a pattern that matches the possible suffix
        # elements that can appear after the '-v{date}' in the
        # image name.
        suffix_pattern = (cls.suffix_pre +
                          cls.ecs +
                          cls.virt_type +
                          cls.ssd +
                          cls.arch +
                          cls.mp_account +
                          cls.gen_id +
                          cls.suffix_post)

        # Combine the above patterns with the uuid prefix and
        # datestamp patterns to contruct a pattern that matches
        # the entire image name.
        pattern = (r'^' +
                   cls.uuid_prefix +
                   basename_pattern +
                   cls.datestamp +
                   suffix_pattern +
                   r'$')

        return re.compile(pattern)

    def __init__(self):
        """Call ``self.matcher()`` class helper method to return a
        compiled RE matcher instance that we cache for subsequent
        re-use."""
        self._matcher = self.matcher()

    def match(self, image_name):
        """Return the result of attempting a ``fullmatch()`` against
        the provided ``image_name`` using the compler matcher."""
        return self._matcher.fullmatch(image_name)
