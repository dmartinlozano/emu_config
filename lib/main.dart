import 'package:emu_config/internet_connection_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart'; 
import 'dark_mode_provider.dart';
import 'emus/emus_provider.dart';
import 'emus/emus_service.dart';
import 'gamepads/gamepads_provider.dart';
import 'gamepads/gamepads_service.dart';
import 'globals.dart';
import 'i18n.dart';
import 'pages/dashboard_page.dart';
import 'services/preferences_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  preferencesService = PreferencesService();
  emusService = EmusService();
  gamepadService = GamepadsService();
  await preferencesService.init();
  await I18n.load(I18n.getLocale());
  await gamepadService.setCustomGamepadController();

  runApp(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => GamepadsProvider()),
          ChangeNotifierProvider(create: (_) => EmusProvider()),
          ChangeNotifierProvider(create: (_) => InternetConnectionProvider()),
          ChangeNotifierProvider(create: (_) => DarkModeProvider()),
        ]
        , child: const MyApp()
      )
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    DarkModeProvider darkModeProvider = Provider.of<DarkModeProvider>(context);
    return MaterialApp(
      title: 'Emu Config',
      home: const DashboardPage(),
      navigatorKey: navigatorKey,
      //theme: darkModeProvider.themeData,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: I18n.supportedLocales,
    );
  }
}
