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


class ImageNameError(Exception):
    """
    Base class for errors thrown by SUSECloudImageName. Any class inheriting
    from it must implement a `message` attribute at the very least.
    """


class APIError(ImageNameError):
    """
    Derived class for exceptions thrown by SUSECloudImageName.

    Attributes:
        message -- relevant error message
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class BadRegexMatchError(APIError):
    """Derived class for image name regex exceptions."""

    def __init__(self, message):
        """Exception raised for a missing fragment.

        Parameters:
            message -- stringified error message
        """
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"


class UndefinedOvalProductError(APIError):
    """Derived class for undefined oval product error exceptions."""

    def __init__(self, message):
        """Exception raised for an undefined oval product name.

        Parameters:
            message -- stringified error message
        """
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"


class UndefinedProductMajorError(APIError):
    """Derived class for undefined product major exceptions."""

    def __init__(self, message):
        """Exception raised for an undefined product major.

        Parameters:
            message -- stringified error message
        """
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"
