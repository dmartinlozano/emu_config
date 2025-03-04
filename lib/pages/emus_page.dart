import 'dart:io';
import 'package:emu_config/globals.dart';
import 'package:emu_config/widgets/emu_state_widget.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:emu_config/emus/emus_provider.dart';
import 'package:emu_config/gamepads/gamepads_provider.dart';
import 'package:emu_config/widgets/options_widget.dart';
import 'package:emu_config/widgets/roms_path_widget.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:accordion/accordion.dart';

class EmusPage extends StatefulWidget {
  const EmusPage({super.key});

  @override
  State<EmusPage> createState() => _EmusPageState();
}

class _EmusPageState extends State<EmusPage> {

  @override
  Widget build(BuildContext context) {
    return Consumer2<EmusProvider, GamepadsProvider>(
      builder: (context, emusProvider, gamepadsProvider, _) {
        return Accordion(
          maxOpenSections: 1,
          headerBorderRadius: 0,
          headerBorderWidth: 1,
          contentBorderWidth: 1,
          contentBorderRadius: 0,
          contentVerticalPadding: 30,
          headerPadding: const EdgeInsets.symmetric(vertical: 10, horizontal: 20),
          headerBackgroundColor: Colors.transparent,
          headerBorderColor: Colors.black,
          headerBorderColorOpened: Colors.black,
          children: emusProvider.emus.map((emu) {
            return AccordionSection(
              isOpen: false,
              header: Text(
                '${emu.name}${emu.platform != null ? ' (${emu.platform})' : ''}',
                style: const TextStyle(color: Colors.black),
              ),
              rightIcon: EmuStateWidget(emu: emu),
              content: Padding(
                padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 10),
                child: Column(
                  children: [
                    if (emu.romsPath != null)
                      RomsPathWidget(emu: emu),
                    if (emu.input != null && gamepadsProvider.gamepads.isNotEmpty)
                      ElevatedButton(
                        onPressed: () => emusService.updateConfig(emu, true), 
                        child: Text("Apply default mapping"))
                      ,
                    if (emu.input != null && 
                        emu.input!.controllerStyleXbox != null &&
                        gamepadsProvider.gamepads.isNotEmpty
                      )
                      ElevatedButton(
                        onPressed: () => emusService.updateConfig(emu, false),
                         child: Text("Change to xbox style")
                      ),
                    if (emu.videoDriver != null)
                      OptionsWidget(
                        emuId: emu.id,
                        title: "Video Driver", 
                        file: emu.videoDriver!.file!, 
                        keyValue: emu.videoDriver!.key!,
                        options: emu.videoDriver!.options!,
                        preferencesKey: "videoDriver"
                      ),
                    if (emu.videoScale != null)
                      OptionsWidget(
                        emuId: emu.id,
                        title: "Video Scale", 
                        file: emu.videoScale!.file!, 
                        keyValue: emu.videoScale!.key!,
                        options: emu.videoScale!.options!,
                        preferencesKey: "videoScale"
                      ),
                    if (emu.hiddeOverlay != null)
                      OptionsWidget(
                        emuId: emu.id,
                        title: "Hidde Overlay", 
                        file: emu.hiddeOverlay!.file!, 
                        keyValue: emu.hiddeOverlay!.key!,
                        options: emu.hiddeOverlay!.options!,
                        preferencesKey: "hiddeOverlay"
                      ),
                    if (emu.region != null)
                      OptionsWidget(
                        emuId: emu.id,
                        title: "Region", 
                        file: emu.region!.file!, 
                        keyValue: emu.region!.key!,
                        options: emu.region!.options!,
                        preferencesKey: "region"
                      ),
                    if (emu.enableSaveStates != null)
                      OptionsWidget(
                        emuId: emu.id,
                        title: "Enable save states", 
                        file: emu.enableSaveStates!.file!, 
                        keyValue: emu.enableSaveStates!.key!,
                        options: emu.enableSaveStates!.options!,
                        preferencesKey: "enableSaveStates"
                      ),
                    if (emu.importProfile != null)
                      ElevatedButton(
                        onPressed: () {
                          showDialog(
                            context: context,
                            builder: (BuildContext context) {
                              return AlertDialog(
                                title: const Text("Import/export mapping manually"),
                                content: Text(emu.importProfile!.description!),
                                actions: [
                                  TextButton(
                                    onPressed: () => Navigator.of(context).pop(),
                                    child: const Text("Cancel"),
                                  ),
                                  TextButton(
                                    onPressed: () async {
                                      Navigator.of(context).pop();
                                      final tempDir = await getTemporaryDirectory();
                                      final tempFile = File('${tempDir.path}/${emu.importProfile?.filename}');
                                      final content = emu.importProfile?.content?.replaceAll("\\n", "\n") ?? "";
                                      await tempFile.writeAsString(content, mode: FileMode.writeOnly, flush: true);
                                      String? selectedDirectory = await FilePicker.platform.getDirectoryPath(dialogTitle: 'Save default profile');
                                      if (selectedDirectory != null)  await tempFile.copy('$selectedDirectory/${emu.importProfile?.filename}');
                                    },
                                    child: const Text("Accept"),
                                  ),
                                ],
                              );
                            },
                          );
                        },
                        child: const Text("Import/export mapping manually"),
                      ),
                  ],
                ),
              ),
            );
          }).toList(),
        );
      },
    );
  }
}
