import 'package:emu_config/emus/class/emu.dart';
import 'package:emu_config/globals.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

// ignore: must_be_immutable
class RomsPathWidget extends StatelessWidget {
  final Emu emu;
  String? selectedDirectory;
  
  RomsPathWidget({super.key, required this.emu});

  @override
  Widget build(BuildContext context) {
    
    selectedDirectory = preferencesService.getValue(emu.id, "romsPath") ?? '';
    TextEditingController controller = TextEditingController(text: selectedDirectory);

    return Row(
      children: [
        Expanded(
          child: TextField(
            key: UniqueKey(),
            controller: controller,
            decoration: InputDecoration(
              labelText: 'Roms Path',
            ),
            readOnly: true,
          ),
        ),
        IconButton(
          icon: Icon(Icons.folder_open),
          onPressed: () async {
            selectedDirectory = await FilePicker.platform.getDirectoryPath();
            if (selectedDirectory != null) {
              preferencesService.setValue(emu.id, "romsPath", selectedDirectory!);
              controller.text = selectedDirectory!;
            }
          },
        ),
      ],
    );
  }
}
