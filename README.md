[![Build Status](https://travis-ci.org/Apstra/aeon-venos.svg?branch=master)](https://travis-ci.org/Apstra/aeon-venos)
[![Coverage Status](https://coveralls.io/repos/github/Apstra/aeon-venos/badge.svg?branch=master)](https://coveralls.io/github/Apstra/aeon-venos?branch=master)
# AEON-VENOS
A Python wrapper module to support various network operating systems.

## Purpose
AEON-VENOS's primary purpose:
 - Create a common Python object model to interact with different vendors' APIs.
 - Gather facts from those devices.
 - Provide a communications channel to push and pull information from those devices.


## Installation
You *MUST* specify extras in order to get the requirements needed to use aeon-venos with your device type. For example:
```
pip install aeon-venos[nxos,eos,cumulus]
```

## Usage
```python
from aeon.eos.device import Device
dev = Device('10.0.0.100', user='user', passwd='passwd')

dev.facts
{'os_name': 'eos', 'vendor': 'arista', 'hw_part_number': None, 'mac_address': u'52:54:00:e8:6c:ca', 
'serial_number': u'525400E86CCA', 'chassis_id': None, 'fqdn': u'localhost.com', 'os_version': u'4.18.4F', 
'virtual': True, 'hw_model': u'vEOS', 'hw_version': u'', 'hw_part_version': None, 'hostname': u'localhost'}

dev.api.execute('show version')
{u'memTotal': 3887540, u'version': u'4.18.4F', u'internalVersion': u'4.18.4F-5927901.4184F', u'serialNumber': u'', 
u'systemMacAddress': u'52:54:00:e8:6c:ca', u'bootupTimestamp': 1506689787.23, u'memFree': 2463080, 
u'modelName': u'vEOS', u'architecture': u'i386', u'isIntlVersion': False, 
u'internalBuildId': u'763e44bf-fb89-4c3e-b735-c373d7a65ee4', u'hardwareRevision': u''}
```

**Automatically determine device type**
```python
from aeon.utils import get_device
dev = get_device('10.0.0.100', user='user', passwd='passwd')
dev.facts
{'os_name': 'eos', 'vendor': 'arista', 'hw_part_number': None, 'mac_address': u'52:54:00:e8:6c:ca', 
'serial_number': u'525400E86CCA', 'chassis_id': None, 'fqdn': u'localhost.com', 'os_version': u'4.18.4F', 
'virtual': True, 'hw_model': u'vEOS', 'hw_version': u'', 'hw_part_version': None, 'hostname': u'localhost'}

```

**Get NOS name only**
```python
from aeon.utils import get_device
get_device('10.0.0.100', user='user', passwd='passwd', nos_only=True)
'eos'
```
