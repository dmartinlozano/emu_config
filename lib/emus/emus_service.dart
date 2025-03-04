import 'dart:convert';
import 'dart:io';
import 'package:emu_config/emus/emus_provider.dart';
import 'package:emu_config/globals.dart';
import 'package:emu_config/gamepads/gamepads_provider.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import 'class/emu.dart';
import 'class/utils.dart';

class EmusService {

  late final GamepadsProvider gamepadsProvider;
  late final EmusProvider emusProvider;

  EmusService(){
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      gamepadsProvider = Provider.of<GamepadsProvider>(navigatorKey.currentContext!, listen: false);
      emusProvider = Provider.of<EmusProvider>(navigatorKey.currentContext!, listen: false);
      String jsonContent = await DefaultAssetBundle.of(navigatorKey.currentContext!).loadString("assets/conf/emus.json");
      emusProvider.emus = (jsonDecode(jsonContent) as List<dynamic>).map((e) => Emu.fromJson(e)).toList();
    });
  }

  Future<bool> isPackageInstalled(String packageId) async {
    try {
      Directory dir = Directory("/storage/emulated/0/Android/data/$packageId");
      return await dir.exists();
    } catch (e) {
      throw Exception('Error checking package: $packageId');
    }
  }

  Future<void> installPackage(Emu emu) async {
    if (emu.source.contains('play.google.com')) {
      final Uri url = Uri.parse(emu.source);
      if (await canLaunchUrl(url)) {
        await launchUrl(url);
      } else {
        throw Exception('Could not launch ${emu.source}');
      }
    } else {
      throw Exception('Unsupported source: ${emu.source}');
    }
  }

  //updateMapper = true: emu.input?.mapper
  //updateMapper = false: emu.input?.controllerStyleXbox
  Future<bool> updateConfig(Emu emu, bool updateMapper) async {

    List<String> lines = await Utils.readConfigFile(emu.input!.file!);
    Map<String, dynamic>? tmp;
    if (emu.input?.mapper != null && updateMapper) {
      tmp = emu.input!.mapper;
    }else if (emu.input?.controllerStyleXbox != null && !updateMapper) {
      tmp = emu.input!.controllerStyleXbox;
    }else{
      return false;
    }
    if (emu.numMaxPlayers > 1){
      final sourceMap = updateMapper ? emu.input!.mapper : (emu.input!.controllerStyleXbox ?? emu.input!.mapper);
      tmp = {
        for (var gamepad in gamepadsProvider.gamepads)
          ...sourceMap.map((key, value) => MapEntry(key.replaceAll("%NUM_PLAYER%", gamepad.numPlayer.toString()), value))
      };
    }
    List<String> updatedLines = [];
    for (String line in lines) {
      final eqIndex = line.indexOf('=');
      if (eqIndex > 0) {
        String key = line.substring(0, eqIndex).trim();
        String value = line.substring(eqIndex + 1).trim();
        if (tmp!.containsKey(key)) value = tmp[key]!.toString();
        updatedLines.add('$key = $value');
      } else {
        updatedLines.add(line);
      }
    }
    await Utils.toFile(updatedLines, emu.input!.file);
    return true;
  }
}
