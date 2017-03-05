from aeon.cumulus.device import Device as CumulusDevice


class Device(CumulusDevice):
    OS_NAME = 'ubuntu'

    def __init__(self, target, **kwargs):
        CumulusDevice.__init__(self, target, **kwargs)
