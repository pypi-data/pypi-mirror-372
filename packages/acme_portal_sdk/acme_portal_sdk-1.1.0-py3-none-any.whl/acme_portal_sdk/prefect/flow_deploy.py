import importlib
import logging
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from prefect.events import (DeploymentCompoundTrigger, DeploymentEventTrigger,
                            DeploymentMetricTrigger, DeploymentSequenceTrigger)

from acme_portal_sdk.flow_deploy import (DeployInfo, DeployInfoPrep,
                                         FlowDeployer)
from acme_portal_sdk.prefect.flow_finder import PrefectFlowFinder


@dataclass
class PrefectDeployInfo(DeployInfo):
    """Dataclass that extends DeployInfo with Prefect-specific deployment configuration

    Attributes:
        triggers: Each key in the dictionary identifies the trigger class and value
            provides the parameters for the trigger type
        image_uri: Docker image URI for the flow deployment
        version: Version identifier for the deployment
        flow_function: The actual flow function object
    """

    triggers: Optional[Dict[str, Dict[Any, Any]]] = None
    image_uri: Optional[str] = None
    version: Optional[str] = None
    flow_function: Optional[Any] = None

    def get_trigger_instances(self) -> List[Any]:
        """
        Convert the triggers dictionary into a list of trigger class instances.

        Returns:
            List[Any]: A list of instantiated trigger objects
        """
        if not self.triggers:
            return []

        # Map trigger name strings to actual classes
        trigger_classes = {
            "DeploymentEventTrigger": DeploymentEventTrigger,
            "DeploymentMetricTrigger": DeploymentMetricTrigger,
            "DeploymentCompoundTrigger": DeploymentCompoundTrigger,
            "DeploymentSequenceTrigger": DeploymentSequenceTrigger,
        }

        result = []
        for trigger_type, params in self.triggers.items():
            if trigger_type in trigger_classes:
                trigger_class = trigger_classes[trigger_type]
                result.append(trigger_class(**params))
            else:
                raise ValueError(f"Unknown trigger type: {trigger_type}")

        return result


class PrefectDeployInfoPrep(DeployInfoPrep):
    """Prepares deployment information from a configuration file and runtime context and standardizes deployment parameters."""

    def __init__(
        self,
        static_flow_deploy_config: Union[Path, str],
        default_work_pool: str,
        prefect_flow_finder: PrefectFlowFinder,
    ):
        self.static_flow_deploy_config = static_flow_deploy_config
        self.default_work_pool = default_work_pool
        self.prefect_flow_finder = prefect_flow_finder
        # Dict with keys being FlowDetails.name and values being dicts of parameters for DeployInfo
        self.config = self._load_yaml_config()

    def _load_yaml_config(self):
        """
        Load the YAML configuration file.

        Returns:
            dict: Parsed YAML configuration
        """
        import yaml

        with open(self.static_flow_deploy_config, "r") as file:
            return yaml.safe_load(file)

    def _import_function(self, module_path, function_name):
        """
        Import a function from a module.

        Args:
            module_path: Path to the module
            function_name: Name of the function in the module

        Returns:
            The imported function
        """
        try:
            # Check if module exists
            if find_spec(module_path) is None:
                raise ImportError(f"Module {module_path} not found")

            # Import module
            module = importlib.import_module(module_path)

            # Get function
            if not hasattr(module, function_name):
                raise AttributeError(
                    f"Function {function_name} not found in {module_path}"
                )

            return getattr(module, function_name)

        except Exception as e:
            logging.error(f"Error importing {function_name} from {module_path}: {e}")
            raise

    def prep_deploy_info(
        self,
        project_name: str,
        branch_name: str,
        commit_hash: str,
        image_uri: str,
        package_version: str,
        env: str,
        flows_to_deploy: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[PrefectDeployInfo]:
        """
        Prepare deployment information from provided context.

        Args:
            project_name: Name of the project
            branch_name: Name of the branch
            commit_hash: Git commit hash
            image_uri: Docker image URI
            package_version: Package version
            env: Environment for deployment
            flows_to_deploy: List of flow names to deploy
            env_vars: Additional environment variables for the deployment

        Returns:
            List[PrefectDeployInfo]: List of prepared deployment information objects
        """
        # Standardize flow names (replace hyphens with underscores)
        std_flows_to_deploy = [
            flow_name.replace("-", "_") for flow_name in flows_to_deploy
        ]

        # Find all available flows and filter to those we want to deploy
        all_flows = self.prefect_flow_finder.find_flows()
        flows_info_to_deploy = [
            flow for flow in all_flows if flow.name in std_flows_to_deploy
        ]

        # Create deployment info objects
        deploy_infos = []
        for flow_info in flows_info_to_deploy:
            # Get flow-specific config if available, otherwise use empty dict
            if flow_info.name in self.config:
                extra_deploy_config = self.config[flow_info.name]
            else:
                extra_deploy_config = {}

            hyphen_flow_name = flow_info.name.replace("_", "-")

            deployment_name = (
                f"{project_name}--{branch_name}--{hyphen_flow_name}--{env}"
            )

            # Create environment variables dictionary
            job_vars = {
                "env": {**(env_vars or {}), "DEPLOYMENT_NAME": deployment_name},
                "image": image_uri,
            }

            # Create tags list
            tags = [
                f"PROJECT_NAME={project_name}",
                f"BRANCH_NAME={branch_name}",
                f"COMMIT_HASH={commit_hash}",
                f"PACKAGE_VERSION={package_version}",
            ]

            # Create version string
            version = f"{branch_name}-{commit_hash}"

            # Import the flow function
            flow_function = self._import_function(
                flow_info.child_attributes["import_path"], flow_info.child_attributes["obj_name"]
            )

            # Standardize flow name if needed
            underscore_flow_name = flow_info.name.replace("-", "_")
            if (
                hasattr(flow_function, "name")
                and flow_function.name != underscore_flow_name
            ):
                logging.info(
                    f"Standardizing flow name {flow_function.name} for deployment to {underscore_flow_name}"
                )
                flow_function.name = underscore_flow_name

            # Create PrefectDeployInfo instance with all required properties
            deploy_info = PrefectDeployInfo(
                name=deployment_name,
                flow_name=flow_info.name,
                work_pool_name=extra_deploy_config.get(
                    "work_pool_name", self.default_work_pool
                ),
                work_queue_name=extra_deploy_config.get("work_queue_name"),
                parameters=extra_deploy_config.get("parameters"),
                job_variables=job_vars,
                cron=extra_deploy_config.get("cron"),
                paused=extra_deploy_config.get("paused", False),
                concurrency_limit=extra_deploy_config.get("concurrency_limit", 1),
                description=extra_deploy_config.get(
                    "description", flow_info.description
                ),
                tags=tags,
                image_uri=image_uri,
                version=version,
                triggers=extra_deploy_config.get("triggers"),
                flow_function=flow_function,
            )
            deploy_infos.append(deploy_info)

        return deploy_infos


class PrefectFlowDeployer(FlowDeployer):
    """Uses the deployment info for desired flows to invoke Prefect flow deployment."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def deploy(self, flow_deploy_info: PrefectDeployInfo) -> None:
        """
        Deploy a Prefect flow using the provided configuration.

        Args:
            flow_deploy_info: Configuration for the deployment including the flow function
        """
        flow_function = flow_deploy_info.flow_function

        if not flow_function:
            self.logger.error(
                f"No flow function found for deployment {flow_deploy_info.name}"
            )
            raise ValueError(
                f"Flow function not set in deploy info for {flow_deploy_info.name}"
            )

        self.logger.info(f"Deploying flow {flow_deploy_info.flow_name}")

        try:
            # Get triggers if defined
            triggers = (
                flow_deploy_info.get_trigger_instances()
                if flow_deploy_info.triggers
                else None
            )

            # Deploy the flow using the configuration from flow_deploy_info
            flow_function.deploy(
                name=flow_deploy_info.name,
                description=flow_deploy_info.description,
                work_pool_name=flow_deploy_info.work_pool_name,
                work_queue_name=flow_deploy_info.work_queue_name,
                cron=flow_deploy_info.cron,
                parameters=flow_deploy_info.parameters,
                job_variables=flow_deploy_info.job_variables,
                image=flow_deploy_info.image_uri,
                tags=flow_deploy_info.tags,
                version=flow_deploy_info.version,
                paused=flow_deploy_info.paused,
                concurrency_limit=flow_deploy_info.concurrency_limit,
                triggers=triggers,
                build=False,
                push=False,
            )

            self.logger.info(f"Successfully deployed flow {flow_deploy_info.name}")

        except Exception as e:
            self.logger.error(f"Error deploying flow {flow_deploy_info.flow_name}: {e}")
            raise
