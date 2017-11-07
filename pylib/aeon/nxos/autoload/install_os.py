# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

__all__ = ['_install_os']


class _install_os(object):
    DESTDIR = 'bootflash'
    VRF_NAME = 'management'

    def __init__(self, device, image=None):
        self.device = device
        self.image = image

    # ##### -------------------------------------------------------------------
    # #####
    # #####                       PROPERTIES
    # #####
    # ##### -------------------------------------------------------------------

    @property
    def md5sum(self):
        """
        Check to see if the file exists on the device
        :return:
        """
        cmd = 'show file {dir}:{bin} md5sum'.format(
            dir=self.DESTDIR, bin=self.image)

        run = self.device.api.exec_opcmd
        try:
            got = run(cmd)
            return got.get('file_content_md5sum').strip()
        except:  # NOQA
            return None

    @property
    def available_space(self):
        cmd = 'df -k /{dir} | grep {dir}'.format(dir=self.DESTDIR)
        run = self.device.api.exec_opcmd
        try:
            got = run(cmd, msg_type='bash')
            return int(got[3])
        except:  # NOQA
            # @@@ TO-DO: need to handle this properly
            raise

    # ##### -------------------------------------------------------------------
    # #####
    # #####                       PUBLIC METHODS
    # #####
    # ##### -------------------------------------------------------------------

    def copy_from(self, location, timeout=10 * 60):
        """
        This method will fetch the image; the fetch will happen from the
        device-side using the 'copy' command.  Note that the NXAPI appears to
        be single-threaded, so the code needs to wait until this operation has
        completed before attempting another API call.  Therefore the :timeout:
        value is set very high (10min)

        :param location: URL to the location of the file.  This URL must be a valid source
        field to the NXOS 'copy' command

        :keyword timeout: Timeout in seconds

        :return:
        """

        cmd = 'copy {location} {dir}: vrf {vrf_name}'.format(
            location=location, dir=self.DESTDIR, vrf_name=self.VRF_NAME)

        run = self.device.api.exec_opcmd
        run(cmd, msg_type='cli_show_ascii', timeout=timeout)

    def run(self, timeout=10 * 60):
        """
        This will invoke the command to install the image, and then
        cause the device to reboot.
        :param timeout: time/seconds to perform the install action
        """

        cmd = 'install all nxos {dir}:{bin}'.format(
            dir=self.DESTDIR, bin=self.image)

        run = self.device.api.exec_opcmd
        run(cmd, msg_type='cli_show_ascii', timeout=timeout)
