from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class DeployInfo:
    """Holds configuration required to deploy a flow.

    Flow deployment contains configuration that defines how to run a unit of work (flow).

    Attributes:
        name: Name of the deployment
        flow_name: Normalized name of the flow to deploy (from FlowDetails.name)
        work_pool_name: Name of the work pool to use for the deployment, controls which group
            of resources is used to execute the flow run
        work_queue_name: Name of the work queue to use for the deployment, controls priority
            of using resources in the pool
        parameters: Parameters to pass to the flow when it runs
        job_variables: Variables to pass to the job when it runs
        cron: Cron schedule for the deployment
        paused: Whether the deployment is in an inactive state
        concurrency_limit: Controls possible number of concurrent flow runs
        description: Description of the deployment, overriding the flow description
        tags: Tags to associate with the deployment, for categorization and filtering
    """

    name: str
    flow_name: str
    work_pool_name: Optional[str] = None
    work_queue_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    job_variables: Optional[Dict] = None
    cron: Optional[str] = None
    paused: Optional[bool] = False
    concurrency_limit: Optional[int] = 1
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DeployInfoPrep(ABC):
    """
    Responsible for preparing and validating deployment information before
    a flow is deployed to a target environment.
    """

    @abstractmethod
    def prep_deploy_info(
        self, *args: List[Any], **kwargs: Dict[Any, Any]
    ) -> List[DeployInfo]:
        """
        Prepare all deployment information needed to deploy.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List[DeployInfo]: A list of DeployInfo objects with the prepared deployment information
        """
        pass


class FlowDeployer(ABC):
    """Deploys flows, with implementations handling the deployment to specific execution environment."""

    @abstractmethod
    def deploy(self, flow_deploy_info: DeployInfo) -> None:
        """
        Deploy a flow.

        Args:
            flow_deploy_info: Configuration for the deployment
        """
        pass


class DeployWorkflow(ABC):
    """Encapsulates the deployment workflow for a flow."""

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """
        Run the deployment workflow for the specified flows.

        This method accepts flexible arguments to allow different implementations
        to require different parameters based on their specific needs.

        Common parameters that implementations may expect:
            flows_to_deploy: List of flow names to deploy
            ref: The git ref (branch/tag) for the workflow
            project_name: Name of the project
            branch_name: Name of the branch
            commit_hash: Git commit hash
            image_uri: Docker image URI
            package_version: Package version
            env: Target environment

        Args:
            *args: Positional arguments specific to the implementation
            **kwargs: Keyword arguments specific to the implementation

        Returns:
            Optional[str]: URL of the deployment if successful, None otherwise
        """
        pass

    def __call__(self, *args: List[Any], **kwargs: Dict[Any, Any]) -> Optional[str]:
        """
        Call the run method with the provided arguments.

        Args:
            **args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Optional[str]: URL of the deployment if successful, None otherwise
        """
        return self.run(*args, **kwargs)
