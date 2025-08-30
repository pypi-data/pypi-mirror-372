import argparse
import sys
import importlib.util
from pathlib import Path
from typing import List, Tuple
from acme_portal_sdk.flow_finder import FlowFinder
from acme_portal_sdk.deployment_finder import DeploymentFinder
from acme_portal_sdk.flow_deploy import DeployWorkflow
from acme_portal_sdk.deployment_promote import PromoteWorkflow


def parse_args():
    parser = argparse.ArgumentParser(
        prog="aps",
        description="SDK to customize behaviour of acme-portal VSCode extension",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add subcommand for checking configuration
    subparsers.add_parser(
        "check-config", help="Check project configuration for the SDK"
    )

    return parser.parse_args()


def check_project_configuration() -> Tuple[bool, List[str]]:
    """
    Checks if the project is configured correctly to use the SDK.

    Returns:
        Tuple[bool, List[str]]: A tuple containing a boolean indicating if the configuration is complete
        and a list of messages detailing the configuration status.
    """
    required_files_to_classes = {
        "flow_finder.py": FlowFinder,
        "deployment_finder.py": DeploymentFinder,
        "flow_deploy.py": DeployWorkflow,
        "deployment_promote.py": PromoteWorkflow,
    }
    sdk_dir = Path(".acme_portal_sdk")
    messages = []
    configuration_complete = True

    for file_name, base_class in required_files_to_classes.items():
        file_path = sdk_dir / file_name
        if not file_path.exists():
            messages.append(f"❌ Missing file: {file_name}")
            configuration_complete = False
        else:
            # Check for an instance of the expected base class in the file
            try:
                spec = importlib.util.spec_from_file_location("module.name", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check for an instance of the expected base class
                expected_instance_found = any(
                    isinstance(value, base_class) for value in module.__dict__.values()
                )

                if not expected_instance_found:
                    messages.append(
                        f"❌ No instance of a class inheriting from {base_class.__name__} found in {file_name}"
                    )
                    configuration_complete = False
                else:
                    messages.append(f"✅ {file_name} is correctly configured.")
            except Exception as e:
                messages.append(f"❌ Error checking {file_name}: {e}")
                configuration_complete = False

    if configuration_complete:
        messages.append("\n✅ Configuration is complete.")
    else:
        messages.append("\n❌ Configuration is incomplete.")

    return configuration_complete, messages


def main_logic(args):
    if args.command == "check-config":
        configuration_complete, messages = check_project_configuration()
        print("\n".join(messages))

        if not configuration_complete:
            print("Please fix the above issues before proceeding.")
            sys.exit(1)


def main():
    args = parse_args()
    main_logic(args)


if __name__ == "__main__":
    main()
