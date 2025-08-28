project(
  'mmcore-test-devices',
  'cpp',
  version: '0.1.0',
  meson_version: '>= 1.2.0',
  default_options: ['cpp_std=c++14', 'prefix=' + meson.current_source_dir()],
)
is_windows = host_machine.system() == 'windows'
is_darwin = host_machine.system() == 'darwin'
cxx = meson.get_compiler('cpp')

if is_darwin
  add_project_arguments('-U_LIBCPP_ENABLE_ASSERTIONS', language: 'cpp')
endif
if cxx.get_id() in ['msvc', 'clang-cl']
  add_project_arguments('-DNOMINMAX', language: 'cpp')
endif

winmm_lib = cxx.find_library('Winmm', required: false)
mmdevice_dep = dependency('mmdevice')
msgpack_dep = dependency('msgpack-cxx', fallback: ['msgpack-cxx', 'msgpack_cxx_dep'])
boost_dep = dependency('boost', fallback: ['boost', 'boost_dep'], include_type: 'system')

if is_windows
  device_cpp_args = [
    '/wd4101', # equivalent to -Wno-unused-but-set-variable
    '/wd5038', # equivalent to -Wno-reorder
    '/wd4624', # equivalent to -Wno-unused-private-field
    '-DNOMINMAX',
  ]
else
  device_cpp_args = [
    '-Wno-unused-but-set-variable',
    '-Wno-reorder',
    '-Wno-unused-private-field',
    '-Wno-return-type',
  ]
endif

# DEMO CAMERA -----------------------------

shared_library(
  'mmgr_dal_DemoCamera',
  ['src/mmCoreAndDevices/DeviceAdapters/DemoCamera/DemoCamera.cpp'],
  cpp_args: device_cpp_args,
  dependencies: [mmdevice_dep, winmm_lib],
  install: true,
)

# UTILITIES --------------------------------

shared_library(
  'mmgr_dal_Utilities',
  sources: [
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/AutoFocusStage.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/ComboXYStage.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/DAGalvo.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/DAMonochromator.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/DAShutter.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/DATTLStateDevice.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/DAXYStage.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/DAZStage.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/MultiCamera.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/MultiDAStateDevice.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/MultiShutter.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/MultiStage.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/SerialDTRShutter.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/SingleAxisStage.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/StateDeviceShutter.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/Utilities/Utilities.cpp',
  ],
  cpp_args: device_cpp_args,
  dependencies: [mmdevice_dep],
  install: true,
)

# NOTIFICATION TESTER ----------------------

shared_library(
  'mmgr_dal_NotificationTester',
  [
    'src/mmCoreAndDevices/DeviceAdapters/NotificationTester/NotificationTester.cpp',
  ],
  cpp_args: device_cpp_args,
  dependencies: [mmdevice_dep],
  install: true,
)

# SEQUENCE TESTER ------------------------

shared_library(
  'mmgr_dal_SequenceTester',
  sources: [
    'src/mmCoreAndDevices/DeviceAdapters/SequenceTester/InterDevice.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/SequenceTester/LoggedSetting.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/SequenceTester/SequenceTester.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/SequenceTester/SettingLogger.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/SequenceTester/TextImage.cpp',
    'src/mmCoreAndDevices/DeviceAdapters/SequenceTester/TriggerInput.cpp',
  ],
  cpp_args: device_cpp_args,
  dependencies: [mmdevice_dep, msgpack_dep, boost_dep],
  install: true,
)

# install MMConfig_demo.cfg into the install directory
install_data('src/MMConfig_demo.cfg', install_dir: get_option('libdir'))