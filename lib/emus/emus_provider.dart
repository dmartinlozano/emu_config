import 'package:flutter/material.dart';

import 'class/emu.dart';

class EmusProvider extends ChangeNotifier {
  
  List<Emu> _emus = [];

  List<Emu> get emus => _emus;

  set emus(List<Emu> value) {
    _emus = value;
    notifyListeners();
  }

  @override
  notifyListeners(){
    super.notifyListeners();
  }
}
