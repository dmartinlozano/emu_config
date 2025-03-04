import 'package:shared_preferences/shared_preferences.dart';

class PreferencesService {
  SharedPreferences? _sp;

  Future<void> init() async {
    _sp = await SharedPreferences.getInstance();
  }

  String? get localeS => _sp?.getString('locale');
  bool? get enabledDarkMode => _sp?.getBool('enabledDarkMode');
  String? getValue(int emuId, String key) => _sp?.getString('${emuId}_$key');

  set localeS(String? localeS) {
    _sp?.setString('locale', localeS!);
  }

  void setValue(int emuId, String key, String value){
    _sp?.setString('${emuId}_$key', value);
  }

  set enabledDarkMode(bool? enabledDarkMode){
    _sp?.setBool('enabledDarkMode', enabledDarkMode!);
  }
}
