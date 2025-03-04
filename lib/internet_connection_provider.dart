import 'dart:async';

import 'package:flutter/material.dart';
import 'package:internet_connection_checker_plus/internet_connection_checker_plus.dart';

class InternetConnectionProvider extends ChangeNotifier{

  StreamSubscription<InternetStatus>? _listener;
  bool _hasInternetConnection = false;

  InternetConnectionProvider(){
    () async {
      _hasInternetConnection  =  await InternetConnection().hasInternetAccess;
      notifyListeners();
    };
    _listener = InternetConnection().onStatusChange.listen((InternetStatus status) {
      switch (status) {
        case InternetStatus.connected:
          _hasInternetConnection = true;
          notifyListeners();
          break;
        case InternetStatus.disconnected:
          _hasInternetConnection = false;
          notifyListeners();
          break;
      }
    });
  }

  bool get hasInternetConnection => _hasInternetConnection;
}