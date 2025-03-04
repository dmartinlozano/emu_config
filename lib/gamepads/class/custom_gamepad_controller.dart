import 'package:gamepads/gamepads.dart';
import 'package:gamepads_platform_interface/method_channel_gamepads_platform_interface.dart';

class CustomGamepadController extends GamepadController {
  CustomGamepadController({
    required super.id,
    required super.name,
    required super.plugin,
    this.descriptor,
    this.vendorId,
    this.productId,
    this.sources,
    required this.isEnabled,
    required this.numPlayer
  });

  factory CustomGamepadController.fromMap(Map<dynamic, dynamic>? map, GamepadController gamepadController) {
    return CustomGamepadController(
      id: gamepadController.id,
      name: gamepadController.name,
      descriptor: map!['descriptor'] as String?,
      vendorId: map['vendorId'] as int?,
      productId: map['productId'] as int?,
      sources: map['sources'] as int?,
      plugin: MethodChannelGamepadsPlatformInterface(), 
      isEnabled: true, 
      numPlayer: null,
    );
  }

  final String? descriptor;
  final int? vendorId;
  final int? productId;
  final int? sources;
  bool isEnabled;
  int? numPlayer;
}
