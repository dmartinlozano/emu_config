import 'package:flutter/material.dart';
import 'gamepads/gamepads_service.dart';
import 'emus/emus_service.dart';
import 'services/preferences_service.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
late GamepadsService gamepadService;
late PreferencesService preferencesService;
late EmusService emusService;
