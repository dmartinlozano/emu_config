import 'dart:async';
import 'dart:io';
import 'package:emu_config/gamepads/class/custom_gamepad_controller.dart';
import 'package:emu_config/globals.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:gamepads/gamepads.dart';
import 'package:path_provider/path_provider.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'class/gamepad_mapping.dart';
import 'gamepads_provider.dart';

class GamepadsService {

  static const platform = MethodChannel('com.dmlv.emu_config/gamepad');
  File? gamecontrollerdbFile;
  StreamSubscription<GamepadEvent>? _subscription;
  GamepadEvent? _event;

  GamepadsService(){
    _subscription = Gamepads.events.listen((event) {
      _event = event;
    });
  }

  setCustomGamepadController() async {
    try {
      WidgetsBinding.instance.addPostFrameCallback((_) async {
        final gamepadsProvider = Provider.of<GamepadsProvider>(navigatorKey.currentContext!, listen: false);
        List<GamepadController> response = await Gamepads.list();
        List<CustomGamepadController> tmp = [];
        for (int i = 0; i < response.length; i++) {
          final Map<dynamic, dynamic>? result = await platform.invokeMethod('getCustomGamepadController', {'gamepadId': int.parse(response[i].id)});
          if (result != null) {
            CustomGamepadController cgc = CustomGamepadController.fromMap(result, response[i]);
            cgc.numPlayer = i+1;
            tmp.add(cgc);
          }
        }
        gamepadsProvider.gamepads = tmp;
      });
    } on PlatformException catch (_) {
      return null;
    }
  }

}
