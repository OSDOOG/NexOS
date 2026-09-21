; Inno Setup Script for NexOS Developer Tools v1.0.0
; Generates NexOS-Developer-Setup.exe

#define MyAppName "NexOS Developer Tools"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "NexOS Operating System Project"
#define MyAppURL "https://github.com/nexos-org/nexos"
#define MyAppExeName "nexos.exe"

[Setup]
AppId={{D37E84B1-398A-421F-8742-5B4B27AE9C12}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\NexOS
DefaultGroupName=NexOS
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE.txt
OutputDir=..\dist_installer
OutputBaseFilename=NexOS-Developer-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full"; Description: "Full installation (Recommended)"
Name: "compact"; Description: "Compact installation (CLI, SDK, NexPack only)"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "cli"; Description: "NexOS Developer CLI (nexos)"; Types: full compact custom; Flags: fixed
Name: "sdk"; Description: "NexOS Application SDK & Headers"; Types: full compact custom; Flags: fixed
Name: "nexpack"; Description: "NexPack Application Packaging Tool (.app)"; Types: full compact custom
Name: "templates"; Description: "Application Project Templates"; Types: full compact custom
Name: "toolchain"; Description: "ESP32-C6 RISC-V Cross-Compiler Toolchain Integration"; Types: full
Name: "docs"; Description: "NexOS Developer Documentation & Quickstart Guides"; Types: full

[Files]
; Binaries
Source: "staging\bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: cli
; SDK
Source: "staging\sdk\*"; DestDir: "{app}\sdk"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: sdk
; CLI Tools
Source: "staging\tools\nexos\*"; DestDir: "{app}\tools\nexos"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: cli
Source: "staging\tools\nex\*"; DestDir: "{app}\tools\nex"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: cli
Source: "staging\targets\*"; DestDir: "{app}\targets"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: cli
; NexPack
Source: "staging\tools\nexpack\*"; DestDir: "{app}\tools\nexpack"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: nexpack
; Templates
Source: "staging\templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: templates
; Documentation
Source: "staging\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: docs

[Tasks]
Name: "addtopath"; Description: "Add NexOS bin directory to system and user PATH environment variable"; GroupDescription: "Environment Settings:"

[Registry]
; Add {app}\bin to system PATH (all users)
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\bin"; \
    Tasks: addtopath; Check: NeedsAddPathHKLM(ExpandConstant('{app}\bin'))

; Add {app}\bin to user PATH
Root: HKCU; Subkey: "Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\bin"; \
    Tasks: addtopath; Check: NeedsAddPath(ExpandConstant('{app}\bin'))

; File association for .app
Root: HKCR; Subkey: ".app"; ValueType: string; ValueName: ""; ValueData: "NexOS.Application"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "NexOS.Application"; ValueType: string; ValueName: ""; ValueData: "NexOS Application Package"; Flags: uninsdeletekey
Root: HKCR; Subkey: "NexOS.Application\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\bin\nexos.cmd"" info ""%1"""

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + UpperCase(Param) + ';', ';' + UpperCase(OrigPath) + ';') = 0;
end;

function NeedsAddPathHKLM(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + UpperCase(Param) + ';', ';' + UpperCase(OrigPath) + ';') = 0;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Do NOT delete user documents or projects!
  end;
end;
