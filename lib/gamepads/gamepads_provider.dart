import 'package:flutter/material.dart';

import 'class/custom_gamepad_controller.dart';

class GamepadsProvider extends ChangeNotifier {

  List<CustomGamepadController> _gamepads = [];

  List<CustomGamepadController> get gamepads => _gamepads;

  set gamepads(List<CustomGamepadController> value) {
    _gamepads = value;
    notifyListeners();
  }

  void updateGamepad(String id, {bool? isEnabled, int? numPlayer}) {
    final index = _gamepads.indexWhere((gamepad) => gamepad.id == id);
    if (index == -1) return;
    final gamepad = _gamepads[index];
    if (isEnabled != null) gamepad.isEnabled = isEnabled;
    if (numPlayer != null) gamepad.numPlayer = numPlayer;
    _gamepads[index] = gamepad;
    notifyListeners();
  }

  void deleteGamepad(String id) {
    _gamepads.removeWhere((gamepad) => gamepad.id == id);
    notifyListeners();
  }
}
