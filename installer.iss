[Setup]
AppId={{749ff07f-5421-4ee7-a1c8-adc252ba2660}
AppName=KomiCAT
AppVersion=1.0.0
AppPublisher=Romi
DefaultDirName={localappdata}\KomiCAT
DefaultGroupName=KomiCAT
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=KomiCAT-Setup-1.0.0
Compression=lzma2
SolidCompression=yes
DiskSpanning=no

[Files]
Source: "dist\KomiCAT\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\KomiCAT"; Filename: "{app}\KomiCAT.exe"
Name: "{autodesktop}\KomiCAT"; Filename: "{app}\KomiCAT.exe"

[Run]
Filename: "{app}\KomiCAT.exe"; Description: "Launch KomiCAT"; Flags: nowait postinstall skipifsilent