from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DeploymentPromote(ABC):
    """Responsible for promoting flows between different environments (e.g., dev to prod), managing the transition of deployments"""

    @abstractmethod
    def promote(
        self,
        project_name: str,
        branch_name: str,
        source_env: str,
        target_env: str,
        flows_to_deploy: List[str],
    ):
        """Promote flows from one environment to another.

        Args:
            project_name: Name of the project
            branch_name: Name of the branch
            source_env: Source environment
            target_env: Target environment
            flows_to_deploy: List of flow names to promote
        """
        pass


class PromoteWorkflow(ABC):
    """Encapsulates the workflow for promoting flows between environments."""

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Run the promotion workflow for the specified flows.

        This method accepts flexible arguments to allow different implementations
        to require different parameters based on their specific needs.

        Common parameters that implementations may expect:
            flows_to_deploy: List of flow names to promote
            source_env: Source environment
            target_env: Target environment
            ref: The git ref (branch/tag) for the workflow
            project_name: Name of the project
            branch_name: Name of the branch

        Args:
            *args: Positional arguments specific to the implementation
            **kwargs: Keyword arguments specific to the implementation

        Returns:
            Optional[str]: URL of the promotion if successful, None otherwise
        """
        pass

    def __call__(self, *args: List[Any], **kwargs: Dict[Any, Any]) -> Optional[str]:
        """Call the run method with the provided arguments.

        Args:
            **args: Positional arguments
            **kwargs: Keyword arguments
        Returns:
            Optional[str]: URL of the promotion if successful, None otherwise
        """
        return self.run(*args, **kwargs)
