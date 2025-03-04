class Emu {
  final int id;
  final String name;
  final String? platform;
  final String package;
  final String source;
  final int numMaxPlayers;
  final Input? input;
  final VideoDriver? videoDriver;
  final VideoScale? videoScale;
  final RomsPath? romsPath;
  final Region? region;
  final EnableSaveStates? enableSaveStates;
  final HiddeOverlay? hiddeOverlay;
  final ImportProfile? importProfile;

  Emu({
    required this.id,
    required this.name,
    this.platform,
    required this.package,
    required this.source,
    required this.numMaxPlayers,
    this.input,
    this.videoDriver,
    this.videoScale,
    this.romsPath,
    this.region,
    this.enableSaveStates,
    this.hiddeOverlay,
    this.importProfile,
  });

  factory Emu.fromJson(Map<String, dynamic> json) {
    return Emu(
      id: json['id'],
      name: json['name'],
      platform: json['platform'],
      package: json['package'],
      source: json['source'],
      numMaxPlayers: json['numMaxPlayers'],
      input: json['input'] != null ? Input.fromJson(json['input']) : null,
      videoDriver: json['videoDriver'] != null ? VideoDriver.fromJson(json['videoDriver']) : null,
      videoScale: json['videoScale'] != null ? VideoScale.fromJson(json['videoScale']) : null,
      romsPath: json['romsPath'] != null ? RomsPath.fromJson(json['romsPath']) : null,
      region: json['region'] != null ? Region.fromJson(json['region']) : null,
      enableSaveStates: json['enableSaveStates'] != null ? EnableSaveStates.fromJson(json['enableSaveStates']) : null,
      hiddeOverlay: json['hiddeOverlay'] != null ? HiddeOverlay.fromJson(json['hiddeOverlay']) : null,
      importProfile: json['importProfile'] != null ? ImportProfile.fromJson(json['importProfile']) : null,
    );
  }
}

class Input {
  final String file;
  final Map<String, dynamic> mapper;
  final Map<String, String>? controllerStyleXbox;

  Input({
    required this.file,
    required this.mapper,
    this.controllerStyleXbox,
  });

  factory Input.fromJson(Map<String, dynamic> json) {
    return Input(
      file: json['file'],
      mapper: Map<String, dynamic>.from(json['mapper']),
      controllerStyleXbox: json['controllerStyleXbox'] != null ? Map<String, String>.from(json['controllerStyleXbox']) : null,
    );
  }
}

class VideoDriver {
  final String? file;
  final String? key;
  final Map<String, String>? options;

  VideoDriver({
    this.file,
    this.key,
    this.options,
  });

  factory VideoDriver.fromJson(Map<String, dynamic> json) {
    return VideoDriver(
      file: json['file'],
      key: json['key'],
      options: json['options'] != null ? Map<String, String>.from(json['options']) : null,
    );
  }
}

class VideoScale {
  final String? file;
  final String? key;
  final Map<String, String>? options;

  VideoScale({
    this.file,
    this.key,
    this.options,
  });

  factory VideoScale.fromJson(Map<String, dynamic> json) {
    return VideoScale(
      file: json['file'],
      key: json['key'],
      options: json['options'] != null ? Map<String, String>.from(json['options']) : null,
    );
  }
}

class RomsPath {
  final String? file;
  final String? key;

  RomsPath({
    this.file,
    this.key,
  });

  factory RomsPath.fromJson(Map<String, dynamic> json) {
    return RomsPath(
      file: json['file'],
      key: json['key'],
    );
  }
}

class Region {
  final String? file;
  final String? key;
  final Map<String, String>? options;

  Region({
    this.file,
    this.key,
    this.options,
  });

  factory Region.fromJson(Map<String, dynamic> json) {
    return Region(
      file: json['file'],
      key: json['key'],
      options: json['options'] != null ? Map<String, String>.from(json['options']) : null,
    );
  }
}

class EnableSaveStates {
  final String? file;
  final String? key;
  final Map<String, String>? options;

  EnableSaveStates({
    this.file,
    this.key,
    this.options,
  });

  factory EnableSaveStates.fromJson(Map<String, dynamic> json) {
    return EnableSaveStates(
      file: json['file'],
      key: json['key'],
      options: json['options'] != null ? Map<String, String>.from(json['options']) : null,
    );
  }
}

class HiddeOverlay {
  final String? file;
  final String? key;
  final Map<String, String>? options;

  HiddeOverlay({
    this.file,
    this.key,
    this.options,
  });

  factory HiddeOverlay.fromJson(Map<String, dynamic> json) {
    return HiddeOverlay(
      file: json['file'],
      key: json['key'],
      options: json['options'] != null ? Map<String, String>.from(json['options']) : null,
    );
  }
}

class ImportProfile {
  final String? filename;
  final String? content;
  final String? description;

  ImportProfile({
    this.filename,
    this.content,
    this.description,
  });

  factory ImportProfile.fromJson(Map<String, dynamic> json) {
    return ImportProfile(
      filename: json['filename'],
      content: json['content'],
      description: json['description'],
    );
  }
}
