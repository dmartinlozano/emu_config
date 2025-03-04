import 'dart:convert';
import 'dart:io';
import 'dart:ui';
import 'package:flutter/services.dart' show rootBundle;

import 'globals.dart';

class I18n {

  I18n._();
  
  static Map<String, dynamic>? _localizedStrings;
  static List<Locale> supportedLocales = const [
    Locale('en'),
    Locale('es'),
  ];

  static Future load(Locale locale) async {
    String jsonContent = await rootBundle.loadString('assets/i18n/${locale.languageCode}.json');
    _localizedStrings = json.decode(jsonContent);
  }

  static String translate(String key) {
    return _localizedStrings?[key] ?? '';
  }

  static Locale getLocale(){
    String? preferencesLocaleS = preferencesService.localeS;
    late Locale defaultLocale = Locale((preferencesLocaleS == null) ? Platform.localeName.split('_')[0] : preferencesLocaleS);
    bool isSupportedDefaultLocale = supportedLocales.any((locale) => locale.languageCode == defaultLocale.languageCode);
    if (!isSupportedDefaultLocale) defaultLocale = const Locale('en'); 
    return defaultLocale;
  }
}