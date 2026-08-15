import plistlib
from pathlib import Path

from monster_deleter_mac.quick_action import build_workflow, install_quick_action


def test_workflow_targets_finder_and_project_launcher(tmp_path: Path) -> None:
    project_root = tmp_path / "Project With Spaces"
    (project_root / "scripts").mkdir(parents=True)
    workflow = build_workflow(project_root)

    metadata = workflow["workflowMetaData"]
    assert metadata["serviceApplicationBundleID"] == "com.apple.finder"
    assert metadata["serviceInputTypeIdentifier"] == "com.apple.Automator.fileSystemObject"

    command = workflow["actions"][0]["action"]["ActionParameters"]["COMMAND_STRING"]
    assert str(project_root / "scripts" / "launch_from_finder.sh") in command
    assert "nohup" in command
    assert "rm " not in command


def test_installed_workflow_is_valid_plist(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    (project_root / "scripts").mkdir(parents=True)
    destination = tmp_path / "Services"

    bundle = install_quick_action(
        project_root,
        destination,
        action_name="Monster Test",
        refresh_services=False,
    )

    document = bundle / "Contents" / "document.wflow"
    with document.open("rb") as file_handle:
        parsed = plistlib.load(file_handle)
    assert parsed["AMDocumentVersion"] == "2"
    assert parsed["actions"][0]["action"]["BundleIdentifier"] == "com.apple.RunShellScript"

