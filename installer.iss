#define MyVer "1.0.0"
#define MyName "learn japanese easy"
#define MyExe "learn japanese easy.exe"
[Setup]
AppId={{1D454AC4-CF7D-4370-BD7A-86F9F5C08E90}
AppName=簡単に日本語を学ぶ — learn japanese easy
AppVersion={#MyVer}
AppVerName=learn japanese easy {#MyVer}
AppPublisher=EX Inc./HYPERION DIGITAL
AppPublisherURL=https://github.com/Teobokki/learn-japanese-easy
AppCopyright=©2026 EX Inc./HYPERION DIGITAL ©2026
VersionInfoVersion={#MyVer}.0
VersionInfoCompany=EX Inc./HYPERION DIGITAL
VersionInfoCopyright=©2026 EX Inc./HYPERION DIGITAL ©2026
VersionInfoProductName=learn japanese easy
VersionInfoDescription=learn japanese easy Setup
DefaultDirName={localappdata}\Programs\{#MyName}
DefaultGroupName=learn japanese easy
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=learn.japanese.easy.Setup.{#MyVer}
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyExe}
UninstallDisplayName=簡単に日本語を学ぶ — learn japanese easy
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "dist\{#MyName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\簡単に日本語を学ぶ — learn japanese easy"; Filename: "{app}\{#MyExe}"
Name: "{group}\Uninstall learn japanese easy"; Filename: "{uninstallexe}"
Name: "{userdesktop}\簡単に日本語を学ぶ — learn japanese easy"; Filename: "{app}\{#MyExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyExe}"; Description: "Open the book now"; Flags: nowait postinstall skipifsilent
