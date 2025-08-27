
"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""
import platform
from nanosurf.lib.devices.i2c.bus_master import I2CBusMaster, I2CChip, I2CInstances, I2CMasterType
from nanosurf.lib.devices.i2c.bus_access import I2CByteMode, I2CBusSpeed, I2COffsetMode, I2CSyncing

if platform.system() == "Linux":
    from nanosurf.lib.devices.i2c.linux_bus_access import I2CBusID
elif platform.system() == "Windows":
    from nanosurf.lib.devices.i2c.windows_bus_access import I2CBusID
    
from nanosurf.lib.devices.i2c.chip_24LC32A import Chip_24LC32A
from nanosurf.lib.devices.i2c.chip_PCA9534 import Chip_PCA9534
from nanosurf.lib.devices.i2c.chip_PCA9548 import Chip_PCA9548
from nanosurf.lib.devices.i2c.chip_TCN75 import Chip_TCN75
from nanosurf.lib.devices.i2c.chip_TMC5031 import Chip_TMC5031
from nanosurf.lib.devices.i2c.chip_TMP42x import Chip_TMP42X
from nanosurf.lib.devices.i2c.chip_MCP45xx import Chip_MCP45XX
from nanosurf.lib.devices.i2c.chip_MAX1161x import Chip_MAX1161x
from nanosurf.lib.devices.i2c.chip_MMA8451 import Chip_MMA8451
from nanosurf.lib.devices.i2c.chip_DS28E07 import Chip_DS28E07
from nanosurf.lib.devices.i2c.chip_SHT45 import Chip_SHT4x
from nanosurf.lib.devices.i2c.chip_TMP119 import Chip_TMP119
from nanosurf.lib.devices.i2c.config_eeprom import ConfigEEPROM

