import 'package:emu_config/globals.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

class DarkModeProvider extends ChangeNotifier{

  ThemeData get themeData{
    bool? enabledDarkMode = preferencesService.enabledDarkMode;
    if (enabledDarkMode == null){
      //get from System
      Brightness brightness = SchedulerBinding.instance.platformDispatcher.platformBrightness;
      enabledDarkMode = brightness == Brightness.dark;
      preferencesService.enabledDarkMode = enabledDarkMode;
    }
    return ThemeData(
      iconTheme: IconThemeData(
        color: (enabledDarkMode == true) ? Colors.white : Colors.black,
      ),
       textTheme: const TextTheme(
        displayLarge: TextStyle(),
        displayMedium: TextStyle(),
        displaySmall: TextStyle(),
        headlineLarge: TextStyle(),
        headlineMedium: TextStyle(),
        headlineSmall: TextStyle(),
        titleLarge: TextStyle(),
        titleMedium: TextStyle(),
        titleSmall: TextStyle(),
        bodyLarge: TextStyle(),
        bodyMedium: TextStyle(),
        bodySmall: TextStyle(),
        labelLarge: TextStyle(),
        labelMedium: TextStyle(),
        labelSmall: TextStyle(),
      ).apply(
        displayColor: (enabledDarkMode == true) ? Colors.white : Colors.black,
        bodyColor: (enabledDarkMode == true) ? Colors.white : Colors.black,
      ),
      listTileTheme: ListTileThemeData(
        textColor: (enabledDarkMode == true) ? Colors.white : Colors.black,
        iconColor: (enabledDarkMode == true) ? Colors.white : Colors.black,
      ),
      dropdownMenuTheme: DropdownMenuThemeData(
        textStyle: TextStyle(color: (enabledDarkMode == true) ? Colors.white : Colors.black)
      ),
      brightness: (enabledDarkMode == true) ? Brightness.dark  : Brightness.light,
    );
  }

  bool get enabledDarkMode => preferencesService.enabledDarkMode ?? false;

  set enabledDarkMode(bool enabledDarkMode){
    preferencesService.enabledDarkMode = enabledDarkMode;
    notifyListeners();
  }
}