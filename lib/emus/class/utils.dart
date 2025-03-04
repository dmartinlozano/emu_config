import 'dart:io';

class Utils {

  static Future<List<String>> readConfigFile(String filePath) async {
    try{
      final inputFile = File(filePath);
      if (!inputFile.existsSync()) throw Exception('$filePath not exists');
      return await File(filePath).readAsLines();
    }catch(_){
      throw Exception('Error to read $filePath');
    }
  }
  static toFile(List<String> lines, String filePath) async {
    await File(filePath).writeAsString(lines.join('\n'));
  }
}