import 'package:emu_config/globals.dart';
import 'package:flutter/material.dart';

class OptionsWidget extends StatefulWidget {
  final String title;
  final String file;
  final String keyValue;
  final Map<String, String> options;
  final String preferencesKey;
  final int emuId;

  const OptionsWidget({super.key, required this.title, required this.file, required this.options, required this.keyValue, required this.preferencesKey, required this.emuId});

  @override
  State<OptionsWidget> createState() => _OptionsWidgetState();
}

class _OptionsWidgetState extends State<OptionsWidget> {
  String? _selectedValue;

  @override
  void initState() {
    super.initState();
    String? savedValue = preferencesService.getValue(widget.emuId, widget.preferencesKey);
    if (savedValue != null && widget.options.containsValue(savedValue)) {
      _selectedValue = savedValue;
    } else {
      _selectedValue = widget.options.values.first;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(widget.title),
        SizedBox(width: 10),
        DropdownButton<String>(
          value: _selectedValue,
          items: widget.options.entries.map((entry) {
            return DropdownMenuItem<String>(
              value: entry.value,
              child: Text(entry.key),
            );
          }).toList(),
          onChanged: (String? newValue) {
            preferencesService.setValue(widget.emuId, widget.preferencesKey, newValue!);
            setState(() {
              _selectedValue = newValue;
            });
          },
        )
      ],
    );
  }
}
