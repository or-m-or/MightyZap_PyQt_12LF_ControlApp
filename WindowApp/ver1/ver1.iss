; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "MightyZap CT01 Actuator Controller"
#define MyAppVersion "1.0"
#define MyAppPublisher "YONG Control, Inc."
#define MyAppExeName "MyProg-x64.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".myp"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{5879F806-063E-41FA-B09C-B81875C7006E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
; "ArchitecturesAllowed=x64compatible" specifies that Setup cannot run
; on anything but x64 and Windows 11 on Arm.
ArchitecturesAllowed=x64compatible
; "ArchitecturesInstallIn64BitMode=x64compatible" requests that the
; install be done in "64-bit mode" on x64 or Windows 11 on Arm,
; meaning it should use the native 64-bit Program Files directory and
; the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=C:\Users\htth8\project\PyQt-Fluent-Widgets-master\PyQt-Fluent-Widgets-master\LICENSE
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=C:\Users\htth8\Desktop
OutputBaseFilename=IC10Controller
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Program Files (x86)\Inno Setup 6\Examples\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\htth8\project\yong_p1\CT01ActuatorControlApp\WindowApp\ver1\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""
;Registry data from file ver1.reg
Root: HKLM; Subkey: "Software\MightyZap_IC10_Controller"; Flags: uninsdeletekeyifempty; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\MightyZap_IC10_Controller"; ValueType: string; ValueName: "InstallPath"; ValueData: "C:\Program Files\MightyZap_IC10_Controller"; Flags: uninsdeletevalue; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\MightyZap_IC10_Controller"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"; Flags: uninsdeletevalue; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\MightyZap_IC10_Controller"; ValueType: string; ValueName: "Publisher"; ValueData: "Yong Control"; Flags: uninsdeletevalue; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\<YourAppName>"; Flags: uninsdeletekeyifempty; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\<YourAppName>"; ValueType: string; ValueName: "DisplayName"; ValueData: "MightyZap_IC10_Controller"; Flags: uninsdeletevalue; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\<YourAppName>"; ValueType: string; ValueName: "UninstallString"; ValueData: "C:\Program Files\MightyZap_IC10_Controller\uninstall.exe"; Flags: uninsdeletevalue; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\<YourAppName>"; ValueType: string; ValueName: "InstallLocation"; ValueData: "C:\Program Files\MightyZap_IC10_Controller"; Flags: uninsdeletevalue; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\<YourAppName>"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "1.0.0"; Flags: uninsdeletevalue; Check: IsAdminInstallMode
;End of registry data from file ver1.reg

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

