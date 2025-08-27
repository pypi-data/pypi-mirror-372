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

from suse_cloud_image_name_parser.regex import SUSECloudImageNameRegexp
from suse_cloud_image_name_parser.errors import (
    BadRegexMatchError,
    UndefinedOvalProductError,
    UndefinedProductMajorError
)

_logger = logging.getLogger(__name__)


class SUSECloudImageName:  # pylint: disable=R0904
    """
    Provides a parser for SUSE cloud image names.

    ``name`` should be a valid image name, such as any of the image names
    reported by ``pint``.

    Given the specified arguments and options, extract relevant
    information fields using the ``SUSECloudImageNameRegexp.matcher()`` helper
    class method.
    """

    def __init__(self, name):
        self._image_name = name

        matched = SUSECloudImageNameRegexp().match(self._image_name)
        try:
            self._image_info = matched.groupdict()
        except AttributeError:
            raise BadRegexMatchError(
                f"Could not match regex for image: {self._image_name}"
            ) from None

        _logger.debug(
            "Image match values for image %s are: %s",
            self._image_name, self._image_info
        )

    @property
    def image_name(self):
        """Get the image_name"""
        return self._image_name

    # Image architecture properties

    @property
    def arch(self):
        """Get the architecture if set, otherwise return a default value"""
        if self._image_info["arch"] in ("x86-64", None):
            return "x86_64"
        return self._image_info["arch"]

    @property
    def is_x86_64(self):
        """Check if image is x86_64"""
        return self.arch == "x86_64"

    @property
    def is_aarch64(self):
        """Check if image is aarch64"""
        return self.is_arm64

    @property
    def is_arm64(self):
        """Check if image is arm64"""
        return self.arch == "arm64"

    @property
    def is_amd64(self):
        """Check if image is amd64 (same as x86_64)"""
        return self.is_x86_64

    @property
    def cloud_arch(self):
        """Get the architecture"""
        if self.is_aarch64:
            return "aarch64"
        if self.is_x86_64:
            return "x86_64"
        return self.arch

    @property
    def leap(self):
        """Get the value of the leap regex match"""
        return self._image_info['leap']

    @property
    def is_leap(self):
        """Check if 'leap' is set"""
        return self.leap is not None

    @property
    def sle_server(self):
        """Get the value of the sle_server regex match"""
        return self._image_info['sle_server']

    @property
    def is_sle_server(self):
        """Check if 'sle_server' is set"""
        return self.sle_server is not None

    @property
    def sle(self):
        """Get the value of the sle regex match"""
        return self._image_info['sle']

    @property
    def is_sle(self):
        """Check if 'sle' is set"""
        return self.sle is not None

    @property
    def suma(self):
        """Get the value of the suma regex match"""
        return self._image_info['suse_manager']

    @property
    def is_suma(self):
        """Check if 'suma' is set"""
        return self.suma is not None

    @property
    def suma_type(self):
        """Get the value of the suma_type regex match"""
        return self._image_info['suma_type']

    @property
    def hpc1(self):
        """Get the value of the hcp1 regex match"""
        return self._image_info['hpc1']

    @property
    def hpc2(self):
        """Get the value of the hpc2 regex match"""
        return self._image_info['hpc2']

    @property
    def is_hpc(self):
        """Check if 'hpc1' or 'hpc2' is set"""
        return (self.hpc1 is not None) or (self.hpc2 is not None)

    @property
    def sap1(self):
        """Get the value of the 'sap1' regex match"""
        return self._image_info['sap1']

    @property
    def sap2(self):
        """Get the value of the 'sap2' regex match"""
        return self._image_info['sap2']

    @property
    def is_sap(self):
        """Check if 'sap1' or 'sap2' is set"""
        return (self.sap1 is not None) or (self.sap2 is not None)

    @property
    def byos(self):
        """Get the value of the 'byos' regex match"""
        return self._image_info['byos']

    @property
    def is_byos(self):
        """Check if 'byos' is set"""
        if self.is_leap:
            return False

        return self.byos is not None

    @property
    def is_payg(self):
        """Check if 'byos' is not set"""
        if self.is_leap:
            return False

        return self.byos is None

    @property
    def basic(self):
        """Get the value of the 'basic' regex match"""
        return self._image_info['basic']

    @property
    def is_basic(self):
        """Check if 'basic' is set"""
        return self.basic is not None

    @property
    def product(self):
        """Get the value of the 'product' regex match"""
        return self._image_info['product']

    @property
    def product_base(self):
        """Get the value of the 'prodbase' regex match"""
        return self._image_info['prodbase']

    @property
    def product_major(self):
        """Get the value of the 'major_version' regex match"""
        return self._image_info['major_version']

    @property
    def product_major_int(self):
        """Determine the product major version as int"""
        if self.product_major is None:

            raise UndefinedProductMajorError(
                f'Product major is undefined for {self._image_name}'
            )

        return int(self.product_major)

    @property
    def product_minor(self):
        """Get the value of the 'minor_version' regex match"""
        min_ver = self._image_info['minor_version']
        if min_ver is not None:
            min_ver = min_ver.lower()
        return min_ver

    @property
    def product_minor_int(self):
        """Determine the product minor version (SPX or .X)"""
        if self.product_minor is None:
            return 0

        return int(self.product_minor.lower().replace('sp', ''))

    @property
    def product_version(self):
        """Determine the product version"""
        joiner = ''
        version = []
        result = None
        version.append(self.product_major)
        if any([
            self.is_hpc,
            self.is_sle_server and self.product_major_int <= 15
        ]):
            joiner = '-'
        elif any([
            self.is_suma,
            self.is_leap,
            self.is_micro,
            self.is_sle_server and self.product_major_int > 15
        ]):
            joiner = '.'

        if self.product_minor:
            version.append(self.product_minor.upper())

        if any(version):
            result = joiner.join(version)

        return result

    @property
    def has_product_version(self):
        """ Check if product_version is set"""
        return self.product_version is not None

    @property
    def product_version_string(self):
        """Set the product version string"""
        if not self.has_product_version:
            return ""
        return self.product_version

    @property
    def product_version_dashed(self):
        """Get the product version using a '-' as separator"""
        return self.product_version_string.replace('.', '-')

    @property
    def product_version_dash_lower(self):
        """Get the lower case product version using a '-' as separator"""
        return self.product_version_string.replace('.', '-').lower()

    @property
    def product_version_lower(self):
        """Get the lower case product version"""
        return self.product_version_string.lower()

    @property
    def product_version_spaced(self):
        """Get the product version using a ' ' as separator"""
        return self.product_version_string.replace('-', ' ')

    # Determine how to maintain these mappings best. maybe in a config file?
    _SUMA_DISTRO = {
        # Keys should be the value of self.product_version
        "4.0": "15-SP1",
        "4.1": "15-SP2",
        "4.2": "15-SP3",
        "4.3": "15-SP4",
        "5.0": "5.5",
        "5.1": "6.1"
    }
    _MICRO_DISTRO = {
        # Keys should be the value of self.product_version
        "5.0": "15-SP2",
        "5.1": "15-SP3",
        "5.2": "15-SP3",
        "5.3": "15-SP4",
        "5.4": "15-SP4",
        "5.5": "15-SP5",
        "6.0": "SL-Framework-One",
        "6.1": "SL-Framework-One"
    }

    @property
    def distro_version(self):
        """
        Determine the distro version for images where the distro
        does not match the product.
        """
        if self.is_suma:
            version = self._SUMA_DISTRO[self.product_version]
        elif self.is_micro:
            version = self._MICRO_DISTRO[self.product_version]
        else:
            version = self.product_version
        return version

    @property
    def has_distro_version(self):
        """Check if the 'distro_version' is set"""
        return self.distro_version is not None

    @property
    def distro_version_string(self):
        """Get the distro version string"""
        if not self.has_distro_version:
            return ""
        return self.distro_version

    @property
    def distro_version_dashed(self):
        """Get 'distro_version-'"""
        return self.distro_version_string.replace('.', '-')

    @property
    def distro_version_lower(self):
        """Get the lowercase of 'distro_version'"""
        return self.distro_version_string.lower()

    @property
    def distro_version_spaced(self):
        """Get 'distro_version' using ' ' as the separator"""
        return self.distro_version_string.replace('-', ' ')

    @property
    def base_name(self):
        """Get the value of the 'base_name' regex match"""
        return self._image_info['base_name']

    @property
    def generic_name(self):
        """Get the generic name of the image"""
        name_parts = [
            self.base_name,
            "-v{date}"
        ]

        if self.has_gen_id:
            name_parts.append(self.suffix.replace(f'-{self.gen_id}', ''))
        else:
            name_parts.append(self.suffix)

        return ''.join(name_parts)

    @property
    def datestamp(self):
        """Get the value of the 'datestamp' regex match"""
        return self._image_info['datestamp']

    @property
    def unique_name(self):
        "Get the unique name of the image"
        name_parts = [
            self.generic_name.format(date=self.datestamp)
        ]

        return '-'.join(name_parts)

    @property
    def uuid_prefix(self):
        """Get the value of the 'uuid_prefix' regex match"""
        return self._image_info['uuid_prefix']

    @property
    def has_uuid_prefix(self):
        """Check if 'uuid_prefix' is set"""
        return self.uuid_prefix is not None

    @property
    def suffix(self):
        """Get the value of the 'suffix' regex match"""
        return self._image_info['suffix']

    @property
    def has_suffix(self):
        """Check if 'suffix' is set"""
        return self.suffix is not None

    @property
    def gen_id(self):
        """Get the value of the 'gen_id' regex match"""
        return self._image_info['gen_id']

    @property
    def has_gen_id(self):
        """Check if 'gen_id' is set"""
        return self.gen_id is not None

    @property
    def chost(self):
        """Get the value of the 'chost' regex match"""
        return self._image_info['chost']

    @property
    def is_chost(self):
        """ Check if 'chost' is set"""
        return self.chost is not None

    @property
    def hardened(self):
        """Get the value of the 'hardened' regex match"""
        return self._image_info['hardened']

    @property
    def is_hardened(self):
        """Check if 'hardened' is set"""
        return self.hardened is not None

    @property
    def micro(self):
        """Get the value of the 'micro' regex match"""
        return self._image_info['micro']

    @property
    def is_micro(self):
        """ Check if 'micro' is set"""
        return self.micro is not None

    @property
    def ecs(self):
        """Get the value of the 'ecs' regex match"""
        return self._image_info['ecs']

    @property
    def is_ecs(self):
        """ Check if 'ecs' is set"""
        return self.ecs is not None

    @property
    def virt_type(self):
        """Get the value of the 'virt_type' regex match"""
        return self._image_info['virt_type']

    @property
    def has_virt_type(self):
        """Get the 'virt_type' if it is set"""
        return self.virt_type is not None

    @property
    def is_hvm(self):
        """ Check if the 'virt_type' is set to hvm"""
        return self.has_virt_type and (self.virt_type == "hvm")

    @property
    def is_pv(self):
        """ Check if the 'virt_type' is set to pv"""
        return self.has_virt_type and (self.virt_type == "pv")

    @property
    def sapcal(self):
        """Get the value of the 'sapcal' regex match"""
        return self._image_info['sapcal']

    @property
    def is_sapcal(self):
        """ Check if the 'sapcal' is set"""
        return self.sapcal is not None

    @property
    def azure_hosted(self):
        """Get the value of the 'azure_hosted' regex match"""
        return self._image_info['azure_hosted']

    @property
    def is_azure_hosted(self):
        """ Check if the 'azure_hosted' is set"""
        return self.azure_hosted is not None

    @property
    def ssd(self):
        """Get the value of the ssd regex match"""
        return self._image_info['ssd']

    @property
    def is_ssd(self):
        """ Check if the 'ssd' is set"""
        return self.ssd is not None

    @property
    def sles(self):
        """Get SLE if product else SLES"""
        if self.is_micro or self.is_hpc:
            return 'SLE'
        return 'SLES'

    @property
    def short_name(self):
        """Get short name used for release notes"""
        if self.is_micro:
            if float(self.product_version) >= 6.2:
                return 'SL-Micro'
            return 'SLE-Micro'
        if self.is_hpc:
            return 'SL-HPC'
        if self.is_sap:
            return 'SLES-SAP'
        if self.is_suma and self.suma_type == 'server':
            if float(self.product_version) >= 5.1:
                return 'multi-linux-manager'
            return 'SUSE-MANAGER'
        if self.is_suma and self.suma_type == 'proxy':
            if float(self.product_version) >= 5.1:
                return 'multi-linux-manager-proxy'
            return 'SUSE-MANAGER-PROXY'
        if self.is_leap:
            return 'OPENSUSE-LEAP'

        return 'SUSE-SLES'

    @property
    def mp_account(self):
        """Get the value of the mp account 'ltd' or 'llc' regex match"""
        return self._image_info['mp_account']

    @property
    def is_ltd(self):
        """ Check if 'ltd' is set as mp account"""
        return self.mp_account and self.mp_account == 'ltd'

    @property
    def is_llc(self):
        """ Check if 'llc' is set as mp account"""
        return self.mp_account and self.mp_account == 'llc'

    @property
    def oval_product(self):
        """Get the name of the oval product corresponding to the image"""
        if self.is_leap:
            return "opensuse.leap." + self.distro_version_string

        if self.is_suma:
            return "suse.manager." + self.product_version

        if self.is_micro:
            if self.product_major_int > 5:
                return "suse.linux.micro." + self.product_version
            return "suse.linux.enterprise.micro." + self.product_version

        if self.is_sle:
            return "suse.linux.enterprise." + self.distro_version_lower

        if self.is_sle_server:
            return "suse.linux.enterprise." + self.product_major

        # Unexpected flags for image name
        raise UndefinedOvalProductError(
            f'Unable to find matching oval_product for {self._image_name}'
        )
