import 'gamepad_mapping.dart';

//@deprecated
class KeyCodeMapper {
  static const Map<String, int> keyCodeMap = {
    'KEYCODE_BUTTON_A': 96,
    'KEYCODE_BUTTON_B': 97,
    'KEYCODE_BUTTON_C': 98,
    'KEYCODE_BUTTON_X': 99,
    'KEYCODE_BUTTON_Y': 100,
    'KEYCODE_BUTTON_Z': 101,
    'KEYCODE_BUTTON_L1': 102,
    'KEYCODE_BUTTON_R1': 103,
    'KEYCODE_BUTTON_L2': 104,
    'KEYCODE_BUTTON_R2': 105,
    'KEYCODE_BUTTON_THUMBL': 106,
    'KEYCODE_BUTTON_THUMBR': 107,
    'KEYCODE_BUTTON_START': 108,
    'KEYCODE_BUTTON_SELECT': 109,
    'KEYCODE_BUTTON_MODE': 110,
    'KEYCODE_BUTTON_1': 188,
    'KEYCODE_BUTTON_2': 189,
    'KEYCODE_BUTTON_3': 190,
    'KEYCODE_BUTTON_4': 191,
    'KEYCODE_DPAD_UP': 19,
    'KEYCODE_DPAD_DOWN': 20,
    'KEYCODE_DPAD_LEFT': 21,
    'KEYCODE_DPAD_RIGHT': 22,
    'AXIS_X': 0, // Generic X axis
    'AXIS_Y': 1, // Generic Y axis
    'AXIS_Z': 11, // Generic Z axis
    'AXIS_RX': 12, // Generic rotation X axis
    'AXIS_RY': 13, // Generic rotation Y axis
    'AXIS_RZ': 14, // Generic rotation Z axis
    'AXIS_LTRIGGER': 17, // Left trigger axis
    'AXIS_RTRIGGER': 18, // Right trigger axis
    'AXIS_HAT_X': 15, // D-pad X axis
    'AXIS_HAT_Y': 16, // D-pad Y axis
  };

  static int? getKeyCode(String keyName) {
    return keyCodeMap[keyName];
  }
}
