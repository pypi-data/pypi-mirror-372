import logging
from typing import Any, Dict, List, Optional

from prefect.client.orchestration import get_client

from acme_portal_sdk.deployment_promote import DeploymentPromote
from acme_portal_sdk.prefect.flow_deploy import (PrefectDeployInfo,
                                                 PrefectDeployInfoPrep,
                                                 PrefectFlowDeployer)


class PrefectDeploymentPromote(DeploymentPromote):
    """Promotes Prefect deployments from one Environment to another."""

    def __init__(
        self,
        deployer: PrefectFlowDeployer,
        flow_deploy_info_prep: PrefectDeployInfoPrep,
    ):
        """
        Initialize the DeploymentPromote with a flow deployer.

        Args:
            deployer: A flow deployer instance to handle the actual deployment
            flow_deploy_info_prep: A helper to prepare deployment info
        """
        self.deployer = deployer
        self.flow_deploy_info_prep = flow_deploy_info_prep
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def _extract_tag_value(tags: List[str], tag_name: str) -> str:
        """
        Extract a value from deployment tags.

        Args:
            tags: List of tags in the format "KEY=VALUE"
            tag_name: The key to extract

        Returns:
            The extracted value string
        """
        matched_tags = [x for x in tags if x.startswith(f"{tag_name}=")]
        if not matched_tags:
            raise ValueError(f"Tag {tag_name} not found in tags: {tags}")
        return matched_tags[0].split("=")[1]

    def _get_source_deployment_info(
        self, project_name: str, branch_name: str, flow_name: str, source_env: str
    ) -> Dict[str, Any]:
        """
        Get information about a source deployment.

        Args:
            project_name: Name of the project
            branch_name: Name of the branch
            flow_name: Name of the flow
            source_env: Source environment name

        Returns:
            Dictionary containing deployment information
        """
        client = get_client(sync_client=True)
        underscore_flow_name = flow_name.replace("-", "_")
        hyphen_flow_name = flow_name.replace("_", "-")

        deployment_name = (
            f"{project_name}--{branch_name}--{hyphen_flow_name}--{source_env}"
        )

        try:
            result = dict(
                client.read_deployment_by_name(
                    f"{underscore_flow_name}/{deployment_name}"
                )
            )
            return result
        except Exception as e:
            self.logger.error(
                f"Error fetching deployment info for `{underscore_flow_name}/{deployment_name}`: {e}"
            )
            raise

    def _prepare_deploy_info(
        self,
        source_deployment_info: Dict[str, Any],
        target_env: str,
        flow_name: str,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[PrefectDeployInfo]:
        """
        Prepare deployment info for promoting a flow from source to target environment.

        Args:
            source_deployment_info: Information about the source deployment
            target_env: Target environment to promote to
            flow_name: Name of the flow to promote
            env_vars: Optional environment variables to set

        Returns:
            List of deployment info objects
        """
        # Extract necessary information from source deployment
        image_uri = source_deployment_info["job_variables"]["image"]
        tags = source_deployment_info["tags"]
        package_version = self._extract_tag_value(tags, "PACKAGE_VERSION")
        commit_hash = self._extract_tag_value(tags, "COMMIT_HASH")
        project_name = self._extract_tag_value(tags, "PROJECT_NAME")
        branch_name = self._extract_tag_value(tags, "BRANCH_NAME")

        # Create deploy info for target environment
        deploy_infos = self.flow_deploy_info_prep.prep_deploy_info(
            project_name=project_name,
            branch_name=branch_name,
            commit_hash=commit_hash,
            image_uri=image_uri,
            package_version=package_version,
            env=target_env,
            flows_to_deploy=[flow_name],
            env_vars=env_vars if env_vars is not None else {},
        )

        return deploy_infos

    def _execute_deployments(self, deploy_infos: List[PrefectDeployInfo]) -> None:
        """
        Execute deployments for the prepared deployment info objects.

        Args:
            deploy_infos: List of deployment info objects to deploy
        """
        for deploy_info in deploy_infos:
            self.deployer.deploy(deploy_info)

    def promote(
        self,
        project_name: str,
        branch_name: str,
        source_env: str,
        target_env: str,
        flows_to_deploy: List[str],
        target_env_vars: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Promote flows from one environment to another.

        Args:
            project_name: Name of the project
            branch_name: Name of the branch
            source_env: Source environment
            target_env: Target environment
            flows_to_deploy: List of flow names to promote
            target_env_vars: Optional environment variables to set for the target environment
        """
        # Standardize flow names
        std_flows_to_deploy = [
            flow_name.replace("-", "_") for flow_name in flows_to_deploy
        ]

        all_deploy_infos = []

        for flow_name in std_flows_to_deploy:
            # Get source deployment info
            source_deployment_info = self._get_source_deployment_info(
                project_name=project_name,
                branch_name=branch_name,
                flow_name=flow_name,
                source_env=source_env,
            )

            # Prepare deployment info for target environment
            deploy_infos = self._prepare_deploy_info(
                source_deployment_info=source_deployment_info,
                target_env=target_env,
                flow_name=flow_name,
                env_vars=target_env_vars,
            )

            all_deploy_infos.extend(deploy_infos)

        # Execute all deployments
        self._execute_deployments(all_deploy_infos)
