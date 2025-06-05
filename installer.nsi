# NSIS script for JXR to JPEG Converter

Name "JXR to JPEG Converter"
OutFile "installer.exe"
InstallDir $PROGRAMFILES\JXRtoJPEG
InstallDirRegKey HKCU "Software\JXRtoJPEG" "Install_Dir"

Page directory
Page instfiles

Section "Install"
  SetOutPath $INSTDIR
  File /r dist\converter_app.exe
  WriteRegStr HKCU "Software\JXRtoJPEG" "Install_Dir" $INSTDIR
  CreateShortCut "$DESKTOP\JXR Converter.lnk" "$INSTDIR\converter_app.exe"
  ${If} $portable == "true"
    ; Portable mode skips registry writes
  ${EndIf}
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\JXR Converter.lnk"
  Delete "$INSTDIR\converter_app.exe"
  RMDir $INSTDIR
  DeleteRegKey HKCU "Software\JXRtoJPEG"
SectionEnd
