from __future__ import annotations

import plistlib
import shlex
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path


DEFAULT_ACTION_NAME = "召唤大将军（Mac）"


def _run_shell_action(command: str) -> dict[str, object]:
    action_uuid = str(uuid.uuid4()).upper()
    input_uuid = str(uuid.uuid4()).upper()
    output_uuid = str(uuid.uuid4()).upper()
    return {
        "action": {
            "AMAccepts": {
                "Container": "List",
                "Optional": False,
                "Types": ["com.apple.cocoa.path"],
            },
            "AMActionVersion": "2.0.3",
            "AMApplication": ["Automator"],
            "AMParameterProperties": {
                "COMMAND_STRING": {},
                "CheckedForUserDefaultShell": {},
                "inputMethod": {},
                "shell": {},
                "source": {},
            },
            "AMProvides": {
                "Container": "List",
                "Types": ["com.apple.cocoa.string"],
            },
            "AMRequiredResources": [],
            "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
            "ActionName": "Run Shell Script",
            "ActionParameters": {
                "COMMAND_STRING": command,
                "CheckedForUserDefaultShell": False,
                "inputMethod": 1,
                "shell": "/bin/zsh",
                "source": "",
            },
            "BundleIdentifier": "com.apple.RunShellScript",
            "CFBundleVersion": "2.0.3",
            "CanShowSelectedItemsWhenRun": False,
            "CanShowWhenRun": True,
            "Category": ["AMCategoryUtilities"],
            "Class Name": "RunShellScriptAction",
            "InputUUID": input_uuid,
            "Keywords": ["Shell", "Script", "Command", "Run", "Unix"],
            "OutputUUID": output_uuid,
            "UUID": action_uuid,
            "UnlocalizedApplications": ["Automator"],
            "arguments": {
                "0": {
                    "default value": 0,
                    "name": "inputMethod",
                    "required": "0",
                    "type": "0",
                    "uuid": "0",
                },
                "1": {
                    "default value": "",
                    "name": "source",
                    "required": "0",
                    "type": "0",
                    "uuid": "1",
                },
                "2": {
                    "default value": False,
                    "name": "CheckedForUserDefaultShell",
                    "required": "0",
                    "type": "0",
                    "uuid": "2",
                },
                "3": {
                    "default value": "",
                    "name": "COMMAND_STRING",
                    "required": "0",
                    "type": "0",
                    "uuid": "3",
                },
                "4": {
                    "default value": "/bin/zsh",
                    "name": "shell",
                    "required": "0",
                    "type": "0",
                    "uuid": "4",
                },
            },
            "isViewVisible": False,
        },
        "isViewVisible": False,
    }


def build_workflow(project_root: Path) -> dict[str, object]:
    launcher = project_root.resolve() / "scripts" / "launch_from_finder.sh"
    launcher_arg = shlex.quote(str(launcher))
    command = (
        'if [ "$#" -gt 0 ]; then\n'
        f"  nohup {launcher_arg} \"$1\" "
        '>>"$HOME/Library/Logs/MonsterDeleterMac.log" 2>&1 &\n'
        "fi"
    )
    return {
        "AMApplicationBuild": "512",
        "AMApplicationVersion": "2.10",
        "AMDocumentVersion": "2",
        "actions": [_run_shell_action(command)],
        "connectors": {},
        "workflowMetaData": {
            "serviceApplicationBundleID": "com.apple.finder",
            "serviceApplicationPath": "/System/Library/CoreServices/Finder.app",
            "serviceInputTypeIdentifier": "com.apple.Automator.fileSystemObject",
            "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
            "serviceProcessesInput": 0,
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
        },
    }


def install_quick_action(
    project_root: Path,
    destination: Path,
    action_name: str = DEFAULT_ACTION_NAME,
    refresh_services: bool = True,
) -> Path:
    destination = destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    target_bundle = destination / f"{action_name}.workflow"

    with tempfile.TemporaryDirectory(prefix="monster-deleter-workflow-") as temp_dir:
        staged_bundle = Path(temp_dir) / target_bundle.name
        contents = staged_bundle / "Contents"
        contents.mkdir(parents=True)

        with (contents / "document.wflow").open("wb") as file_handle:
            plistlib.dump(build_workflow(project_root), file_handle, fmt=plistlib.FMT_XML)

        info = {
            "CFBundleIdentifier": "local.monsterdeleter.mac.quickaction",
            "CFBundleName": action_name,
            "CFBundlePackageType": "Wflow",
            "CFBundleShortVersionString": "0.2.0",
            "CFBundleVersion": "1",
        }
        with (contents / "Info.plist").open("wb") as file_handle:
            plistlib.dump(info, file_handle, fmt=plistlib.FMT_XML)

        if target_bundle.exists():
            shutil.rmtree(target_bundle)
        shutil.copytree(staged_bundle, target_bundle)

    if refresh_services and Path("/System/Library/CoreServices/pbs").exists():
        subprocess.run(
            ["/System/Library/CoreServices/pbs", "-flush"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return target_bundle


def uninstall_quick_action(
    destination: Path,
    action_name: str = DEFAULT_ACTION_NAME,
    refresh_services: bool = True,
) -> bool:
    target_bundle = destination.expanduser().resolve() / f"{action_name}.workflow"
    if not target_bundle.exists():
        return False

    shutil.rmtree(target_bundle)
    if refresh_services and Path("/System/Library/CoreServices/pbs").exists():
        subprocess.run(
            ["/System/Library/CoreServices/pbs", "-flush"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return True
