import 'package:emu_config/globals.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../gamepads/gamepads_provider.dart';
import '../gamepads/class/custom_gamepad_controller.dart';

class GamepadsPage extends StatefulWidget {
  const GamepadsPage({super.key});

  @override
  State<GamepadsPage> createState() => _GamepadsPageState();
}

class _GamepadsPageState extends State<GamepadsPage> {

  @override
  Widget build(BuildContext context) {
    return Consumer<GamepadsProvider>(
      builder: (context, gamepadsProvider, _) {
        return Padding(
          padding: const EdgeInsets.all(8.0),
          child: ListView.builder(
            itemCount: gamepadsProvider.gamepads.length,
            itemBuilder: (context, index) {
              final gamepad = gamepadsProvider.gamepads[index];
              return Dismissible(
                key: Key(gamepad.id.toString()),
                direction: DismissDirection.startToEnd,
                onDismissed: (direction) {
                  gamepadsProvider.deleteGamepad(gamepad.id);
                },
                background: Container(
                  color: Colors.red,
                  alignment: Alignment.centerLeft,
                  padding: const EdgeInsets.only(left: 20.0),
                  child: const Icon(Icons.delete, color: Colors.white),
                ),
                child: Column(
                  children: [
                    GestureDetector(
                      onTap: () {
                        setState(() {
                          // Swap the gamepad at the tapped index with the first gamepad in the list
                          if (index > 0) {
                            final CustomGamepadController temp = gamepadsProvider.gamepads[0];
                            final int? tempNumPlayer = gamepadsProvider.gamepads[0].numPlayer;
                            gamepadsProvider.gamepads[0] = gamepadsProvider.gamepads[index];
                            gamepadsProvider.gamepads[0].numPlayer = tempNumPlayer;
                            gamepadsProvider.gamepads[index] = temp;
                            gamepadsProvider.gamepads[index].numPlayer = tempNumPlayer;

                            gamepadsProvider.updateGamepad(
                              gamepadsProvider.gamepads[0].id,
                              numPlayer: gamepadsProvider.gamepads[0].numPlayer,
                            );
                            gamepadsProvider.updateGamepad(
                              gamepadsProvider.gamepads[index].id,
                              numPlayer: gamepadsProvider.gamepads[index].numPlayer,
                            );
                          }
                        });
                      },
                      child: ListTile(
                        title: Text(gamepad.name),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.drag_handle),
                          ],
                        ),
                      ),
                    ),
                    const Divider(
                      height: 1,
                      color: Colors.grey,
                    ),
                  ],
                ),
              );
            },
          ),
        );
      },
    );
  }
}
