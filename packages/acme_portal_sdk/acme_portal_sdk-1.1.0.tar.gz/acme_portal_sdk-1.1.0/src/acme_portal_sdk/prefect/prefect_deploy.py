import argparse
import logging
import sys
from pathlib import Path
from typing import List

from acme_config import add_main_arguments, load_saved_parameters
from acme_portal_sdk.prefect.flow_deploy import (
    PrefectDeployInfoPrep,
    PrefectFlowDeployer,
)
from acme_portal_sdk.prefect.deployment_promote import PrefectDeploymentPromote

logger = logging.getLogger(__name__)

DEFAULT_WORK_POOL = "ecs-pool"


def import_flow_finder():
    """
    Import the flow_finder instance, ensuring the .acme_portal_sdk directory
    is in the Python path first.

    Returns:
        The flow_finder instance from .acme_portal_sdk/flow_finder.py
    """
    # Find the project root directory (where .acme_portal_sdk should exist)
    project_root = Path.cwd()  # todo: should this be passed from command line?
    acme_portal_sdk_path = project_root / ".acme_portal_sdk"

    # Make sure the path exists
    if not acme_portal_sdk_path.exists():
        raise ImportError(
            f".acme_portal_sdk directory not found at: {acme_portal_sdk_path}"
        )

    # Add to Python path if not already there
    str_path = str(acme_portal_sdk_path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

    # Now we can safely import the flow_finder
    try:
        from flow_finder import flow_finder

        return flow_finder
    except ImportError as e:
        logger.error(f"Failed to import flow_finder: {e}")
        raise ImportError(
            f"Could not import flow_finder from {acme_portal_sdk_path}/flow_finder.py"
        ) from e


def parse_args():
    parser = argparse.ArgumentParser(description="Deploy flows to prefect")
    subparsers = parser.add_subparsers(dest="command")
    # Deploy parser for initial deployment
    deploy_parser = subparsers.add_parser("deploy")
    add_main_arguments(deploy_parser)
    deploy_parser.add_argument(
        "-project-name",
        type=lambda x: str(x).replace("_", "-"),
        required=True,
        help="Name of the project",
    )
    deploy_parser.add_argument(
        "-branch-name",
        type=lambda x: str(x).replace("_", "-"),
        required=True,
        help="Name of the branch",
    )
    deploy_parser.add_argument(
        "-commit-hash", type=str, required=True, help="Git commit hash"
    )
    deploy_parser.add_argument("-image-uri", type=str, required=True, help="Image URI")
    deploy_parser.add_argument(
        "-package-version", type=str, required=True, help="Package version"
    )
    deploy_parser.add_argument(
        "-static-flow-config-path",
        type=str,
        required=True,
        help="Path to static flow deployment configuration file",
    )
    deploy_parser.add_argument(
        "--flows-to-deploy",
        type=str,
        default="all",
        help="Comma separated list of flow config names to deploy, or 'all'",
    )

    # Promote parser for promoting deployment from one environment to another
    promote_parser = subparsers.add_parser("promote")
    add_main_arguments(promote_parser)
    promote_parser.add_argument(
        "-source-env", type=str, required=True, help="Source environment"
    )
    promote_parser.add_argument(
        "-project-name",
        type=lambda x: str(x).replace("_", "-"),
        required=True,
        help="Name of the project",
    )
    promote_parser.add_argument(
        "-branch-name",
        type=lambda x: str(x).replace("_", "-"),
        required=True,
        help="Name of the branch",
    )
    promote_parser.add_argument(
        "-static-flow-config-path",
        type=str,
        required=True,
        help="Path to static flow deployment configuration file",
    )
    promote_parser.add_argument(
        "--flows-to-deploy",
        type=str,
        default="all",
        help="Comma separated list of flow config names to deploy, or 'all'",
    )

    return parser.parse_args()


def deploy(args):
    # Load environment variables
    env_vars = load_saved_parameters(args.app_name, args.env, args.ver_number)

    # Get the flow_finder instance
    flow_finder = import_flow_finder()

    # Initialize deploy info prep and deployer
    deploy_info_prep = PrefectDeployInfoPrep(
        static_flow_deploy_config=args.static_flow_config_path,
        default_work_pool=DEFAULT_WORK_POOL,
        prefect_flow_finder=flow_finder,
    )
    deployer = PrefectFlowDeployer()

    # Determine which flows to deploy
    flows_to_deploy = _get_flows_to_deploy(args.flows_to_deploy, flow_finder)

    # Prepare deployment info
    deploy_infos = deploy_info_prep.prep_deploy_info(
        project_name=args.project_name,
        branch_name=args.branch_name,
        commit_hash=args.commit_hash,
        image_uri=args.image_uri,
        package_version=args.package_version,
        env=args.env,
        flows_to_deploy=flows_to_deploy,
        env_vars=env_vars,
    )

    # Execute deployments
    for deploy_info in deploy_infos:
        deployer.deploy(deploy_info)


def _get_flows_to_deploy(flows_arg: str, flow_finder=None) -> List[str]:
    """
    Determine which flows to deploy based on input argument.

    Args:
        flows_arg: String containing flow names or 'all'
        flow_finder: Optional flow finder instance, will be imported if None

    Returns:
        List of flow names to deploy
    """
    if flows_arg == "all":
        # Import flow_finder if not provided
        if flow_finder is None:
            flow_finder = import_flow_finder()

        # Get all available flows
        all_flows = flow_finder.find_flows()
        return [flow.name for flow in all_flows]
    else:
        return flows_arg.split(",")


def promote(args):
    # Load environment variables
    env_vars = load_saved_parameters(args.app_name, args.env, args.ver_number)

    # Get the flow_finder instance
    flow_finder = import_flow_finder()

    # Initialize deploy info prep and deployer
    deploy_info_prep = PrefectDeployInfoPrep(
        static_flow_deploy_config=args.static_flow_config_path,
        default_work_pool=DEFAULT_WORK_POOL,
        prefect_flow_finder=flow_finder,
    )
    deployer = PrefectFlowDeployer()

    # Create the promotion handler
    promotion_handler = PrefectDeploymentPromote(
        deployer=deployer, flow_deploy_info_prep=deploy_info_prep
    )

    # Determine which flows to promote
    flows_to_promote = _get_flows_to_deploy(args.flows_to_deploy, flow_finder)

    # Execute the promotion
    promotion_handler.promote(
        project_name=args.project_name,
        branch_name=args.branch_name,
        source_env=args.source_env,
        target_env=args.env,
        flows_to_deploy=flows_to_promote,
        target_env_vars=env_vars,
    )


def main_logic(args):
    if args.command == "deploy":
        deploy(args)
    elif args.command == "promote":
        promote(args)
    else:
        raise ValueError(f"Invalid command: {args.command}")


def main():
    args = parse_args()
    main_logic(args)


if __name__ == "__main__":
    main()
