### 0.5.0
- Add controllable base class
- Add discovery module

### 0.4.8
- Revert some changes from 0.4.6 related to the default values from ScanData model

### 0.4.7
- Remove redundant data models

### 0.4.6
- Fix tuple concatination for RGBW color property
- Replace optional parts with default values in ScanData model
- Add some properties to DALIScan class
- Add Device helper methods for most used controls

### 0.4.5
- Change dependency version constraints to be less strict

### 0.4.4
- Fix type annotation in ScanData model
- Remove property setters from sensors/zones classes

### 0.4.3
- Bump aiohttp version to be compatible with Home Assistant 2025.8.x

### 0.4.2
- Bump pydantic version to be compatible with Home Assistant 2025.7.x

### 0.4.1
- Add some project metadata

### 0.4.0
- Remove delete methods from Devices/Sensors/Zones classes
- Remove option to initialise DALIScan/Devices/Info/Sensors/Zones classes with data
- Remove general APIClient class
- Add control broadcast/group classes
- Add helper methods for certain requests to Auth class
- Update tests
- Update project name

### 0.3.3
- Update models to v1.14.1

### 0.3.2
- Add default values for various models
- Fix some type annotations in models
- Add more properties to Devices, Sensors and Zones classes
- Remove get_device, get_sensor and get_zone methods

### 0.3.1
- Remove Device.is_dimmable property
- Add class properties to access most used informations

### 0.3.0
- Fix features model validation issues
- Switch to uv virtualenv/dependency management
- Update package dependencies
- Update to Python version 3.13
- Remove pydantic v1 compatibility
- Add missing color features to control model

### 0.2.0
- Add missing default values for optional variables in models
- Rename DALI device type enum keys
- Add objects to handle zone(s)
- Add objects to handle sensor(s)
- Fix property names in ColorXY model
- Change that integers are allowed as DALI device types

### 0.1.4
- Replace dimmable type in DeviceFeatures model with float

### 0.1.3
- Fix data not being serializable by pydantic if using sets

### 0.1.2
- Fix typo in StartScanData model

### 0.1.1
- Fix Device.is_dimmable property always returning false

### 0.1.0
- Initial version
