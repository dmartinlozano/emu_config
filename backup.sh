#!/bin/bash

packages=(
  "com.flycast.emulator"
  "info.cemu.Cemu"
  "org.devmiyax.yabasanshioro2.pro"
  "org.ppsspp.ppsspp"
  "com.github.stenzek.duckstation"
  "io.recompiled.redream"
  "org.dolphinemu.dolphinemu"
  "org.vita3k.emulator"
  "com.retroarch.aarch64"
  "me.magnum.melonds"
  "org.mupen64plusae.v3.fzurita"
)
backup_dir="backup"
mkdir -p "$backup_dir"

adb devices

if [ $(adb devices | grep -w "device" | wc -l) -eq 0 ]; then
  echo "No device detected."
  exit 1
fi

for package in "${packages[@]}"; do
  source_path="/storage/emulated/0/Android/data/$package"
  
  if adb shell [ -d "$source_path" ]; then
    mkdir -p "$backup_dir/$package"
    echo "Backing up $package..."
    adb pull "$source_path" "$backup_dir/$package/"
    
    if [ $? -eq 0 ]; then
      echo "Backup of $package completed successfully."
    else
      echo "Error backing up $package."
    fi
  else
    echo "Folder $source_path does not exist on the device."
  fi
done

echo "Backup finished."
