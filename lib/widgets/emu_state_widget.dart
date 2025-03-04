import 'dart:io';

import 'package:emu_config/internet_connection_provider.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../emus/class/emu.dart';
import '../emus/emus_provider.dart';

enum EmuState {
  installed,
  uninstalled,
  notInternetConnection
}

class EmuStateWidget extends StatefulWidget {

  Emu emu;

  EmuStateWidget({super.key, required this.emu});

  @override
  State<EmuStateWidget> createState() => _EmuStateWidgetState();
}

class _EmuStateWidgetState extends State<EmuStateWidget> {

  Future<bool> isInstaled(String package) async {
    return await Directory('/storage/emulated/0/Android/data/$package').exists();
  }

  Future<void> _installEmu() async {
    await launchUrl(Uri.parse(widget.emu.source));
  }

  @override
  Widget build(BuildContext context) {
    WidgetsFlutterBinding.ensureInitialized();
    return Consumer2<InternetConnectionProvider, EmusProvider>(
      builder: (context, internetConnectionProvider, emusProvider, _) {
        return FutureBuilder<bool>(
          future: isInstaled(widget.emu.package),
          builder: (BuildContext context, AsyncSnapshot<bool> snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const CircularProgressIndicator();
            } else {
              if (snapshot.data!) {
                return const Icon(Icons.expand_more, color: Colors.black);
              } else if (!internetConnectionProvider.hasInternetConnection) {
                return IconButton(
                  icon: const Icon(Icons.report_gmailerrorred_rounded, color: Colors.red),
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (BuildContext context) {
                        return AlertDialog(
                          title: const Text("No Internet Connection"),
                          content: const Text("Install the emulator manually"),
                          actions: <Widget>[
                            TextButton(
                              child: const Text("Accept"),
                              onPressed: () {
                                Navigator.of(context).pop();
                              },
                            ),
                          ],
                        );
                      },
                    );
                  },
                );
              } else {
                return ElevatedButton(
                  child: const Text("Install"),
                  onPressed: () => _installEmu(),
                );
              }
            }
          },
        );
      },
    );
  }
}
