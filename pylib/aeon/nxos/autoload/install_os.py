from aeon import exceptions

__all__ = ['_install_os']


class _install_os(object):
    DESTDIR = 'bootflash'

    def __init__(self, device, filepath=None):
        self.device = device

        self._binfile = None
        self._filepath = None

        self.filepath = filepath

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        self._filepath = filepath
        self._binfile = filepath.rpartition('/')[2] if filepath else None

    @property
    def md5sum(self):
        """
        Check to see if the file exists on the device
        :return:
        """
        cmd = 'show file {dir}:{bin} md5sum'.format(
            dir=self.DESTDIR, bin=self._binfile)

        run = self.device.api.exec_opcmd
        got = run(cmd)
        return None if not got else got.get('file_content_md5sum').strip()

    @property
    def available_space(self):
        cmd = 'df -k /{dir} | grep bootflash'.format(dir=self.DESTDIR)
        run = self.device.api.exec_opcmd
        got = run(cmd, msg_type='bash')
        try:
            av_sz = int(got[3])
        except:
            # @@@ TO-DO: need to handle this properly
            raise
        return av_sz

    def copy_from(self, location, timeout=1):
        """
        This method will fetch the image; the fetch will happen from the device-side
        using the 'copy' command
        :param location: URL to the location of the file.  This URL must be a valid source
        field to the NXOS 'copy' command
        :return:
        """

        cmd = 'copy {location}/{image} {dir}: vrf management'.format(
            location=location, image=self._binfile, dir=self.DESTDIR)

        run = self.device.api.exec_opcmd
        try:
            run(cmd, msg_type='cli_show_ascii', timeout=timeout)

        except exceptions.TimeoutError as exc:
            pass

        except Exception as exc:
            raise exc

    def run(self, timeout=5*60):
        """
        This will invoke the command to install the image, and then
        cause the device to reboot.
        :param timeout: time/seconds to perform the install action
        """

        cmd = 'install all nxos {dir}:{bin}'.format(
            dir=self.DESTDIR, bin=self._binfile)

        run = self.device.api.exec_opcmd
        try:
            run(cmd, msg_type='cli_show_ascii', timeout=timeout)
        except:
            raise
