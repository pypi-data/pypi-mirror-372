import json
import os
import subprocess
import time
from typing import Dict, List, Optional, Tuple

from ..deployment_promote import PromoteWorkflow
from ..flow_deploy import DeployWorkflow


class CommandExecutor:
    """Executes shell commands and returns their output."""

    def execute(
        self, command: str, working_dir: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Execute a shell command and return its output.

        Args:
            command: The command to execute
            working_dir: The directory to run the command in

        Returns:
            Tuple of (stdout, stderr) from the command
        """
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir,
            text=True,
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, command, stdout, stderr
            )

        return stdout, stderr


class GitService:
    """Provides Git-related functionality."""

    def __init__(self, command_executor: CommandExecutor):
        self.command_executor = command_executor

    def get_repository_url(self, working_dir: Optional[str] = None) -> Optional[str]:
        """
        Get the URL of the Git repository.

        Args:
            working_dir: The directory to run the Git command in

        Returns:
            The URL of the repository or None if not found
        """
        try:
            # Get the remote URL
            stdout, _ = self.command_executor.execute(
                "git remote get-url origin", working_dir
            )
            remote_url = stdout.strip()

            # Convert SSH URL to HTTPS URL if needed
            if remote_url.startswith("git@github.com:"):
                remote_url = remote_url.replace(
                    "git@github.com:", "https://github.com/"
                )
                if remote_url.endswith(".git"):
                    remote_url = remote_url[:-4]

            return remote_url
        except (subprocess.CalledProcessError, Exception) as e:
            print(f"Error getting repository URL: {e}")
            return None


class GitHubWorkflowService:
    """Service for GitHub workflow operations."""

    def __init__(self, command_executor: CommandExecutor, git_service: GitService):
        self.command_executor = command_executor
        self.git_service = git_service
        self._verify_gh_cli_installed()

    def _verify_gh_cli_installed(self) -> None:
        """
        Verify that GitHub CLI (gh) is installed and available.

        Raises:
            RuntimeError: If GitHub CLI is not installed or not accessible
        """
        try:
            self.command_executor.execute("gh --version")
        except subprocess.CalledProcessError:
            raise RuntimeError(
                "GitHub CLI (gh) is not installed or not in PATH. "
                "Please install it from https://cli.github.com/ to use this service."
            )
        except Exception as e:
            raise RuntimeError(f"Error verifying GitHub CLI installation: {e}")

    def trigger_workflow(
        self,
        workflow_file: str,
        workflow_inputs: Dict[str, str],
        workflow_ref: str = "main",
    ) -> Optional[str]:
        """
        Trigger a GitHub workflow.

        Args:
            workflow_file: The workflow file name
            workflow_inputs: The inputs for the workflow
            workflow_ref: The git ref (branch/tag) for the workflow

        Returns:
            URL to the workflow run or None on error
        """
        try:
            run_url = self.trigger_workflow_via_github_cli(
                workflow_file, workflow_inputs, workflow_ref
            )
            return run_url
        except Exception as e:
            print(f"Error triggering GitHub workflow: {e}")
            return None

    def trigger_workflow_via_github_cli(
        self, workflow_file: str, workflow_inputs: Dict[str, str], workflow_ref: str
    ) -> Optional[str]:
        """
        Trigger a GitHub workflow using the GitHub CLI.

        Args:
            workflow_file: The workflow file name
            workflow_inputs: The inputs for the workflow
            workflow_ref: The git ref (branch/tag) for the workflow

        Returns:
            URL to the workflow run or None on error
        """
        try:
            # Format workflow inputs for CLI command
            input_args = " ".join(
                [f"-f {key}={value}" for key, value in workflow_inputs.items()]
            )

            # Run the workflow using GitHub CLI
            command = f"gh workflow run {workflow_file} -r {workflow_ref} {input_args}"
            stdout, _ = self.command_executor.execute(command)
            print("Workflow triggered, getting run info...")

            # Wait briefly to ensure the workflow has been registered
            time.sleep(2)

            # Get the workflow name from the file path
            workflow_name = os.path.basename(workflow_file)

            # Get the list of runs for this workflow
            list_command = f"gh run list --workflow={workflow_name} --limit=1 --json databaseId,url"
            stdout, _ = self.command_executor.execute(list_command)

            return self.parse_workflow_run_response(stdout)
        except Exception as e:
            print(f"Error using GitHub CLI: {e}")
            return None

    def parse_workflow_run_response(self, run_list_output: str) -> Optional[str]:
        """
        Parse the GitHub CLI response for workflow run information.

        Args:
            run_list_output: The output from the GitHub CLI run list command

        Returns:
            URL to the workflow run or None
        """
        try:
            run_data = json.loads(run_list_output)
            if run_data and len(run_data) > 0:
                latest_run = run_data[0]
                if "url" in latest_run and latest_run["url"]:
                    print(f"Workflow triggered via CLI: {latest_run['url']}")
                    return latest_run["url"]
                elif "databaseId" in latest_run:
                    # Construct URL manually if only ID is available
                    repo_url = self.git_service.get_repository_url()
                    if repo_url:
                        run_url = f"{repo_url}/actions/runs/{latest_run['databaseId']}"
                        print(f"Workflow triggered via CLI: {run_url}")
                        return run_url

            print("Failed to get workflow run URL from CLI output")
            return None
        except Exception as e:
            print(f"Error parsing workflow run data: {e}")
            return None


class GithubActionsDeployWorkflow(DeployWorkflow):
    """Implements the DeployWorkflow interface using GitHub Actions"""

    def __init__(self, workflow_file: str = "deploy.yml", default_ref: str = "main"):
        """
        Initialize the GitHub Actions deploy workflow.

        Args:
            workflow_file: The workflow file name (default: deploy.yml)
            default_ref: Default git ref to use if none provided in run() (default: main)
        """
        self.workflow_file = workflow_file
        self.default_ref = default_ref
        self.command_executor = CommandExecutor()
        self.git_service = GitService(self.command_executor)
        self.workflow_service = GitHubWorkflowService(
            self.command_executor, self.git_service
        )

    def run(self, flows_to_deploy: List[str], ref: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Run the deployment workflow for the specified flows using GitHub Actions.

        Args:
            flows_to_deploy: List of flow names to deploy
            ref: The git ref (branch/tag) for the workflow (optional, uses default_ref if not provided)
            **kwargs: Additional workflow parameters (for future extensibility)

        Returns:
            Optional[str]: URL of the workflow run if successful, None otherwise
        """
        # Use default ref if none provided
        if ref is None:
            ref = getattr(self, 'default_ref', 'main')

        # Convert list to comma-separated string for GitHub Actions input
        flows_str = ",".join(flows_to_deploy)

        # Prepare workflow inputs
        workflow_inputs = {"flows-to-deploy": flows_str}

        # Trigger the workflow
        run_url = self.workflow_service.trigger_workflow(
            self.workflow_file, workflow_inputs, ref
        )

        if run_url:
            print(
                f"Deployment workflow triggered successfully. You can monitor it at: {run_url}"
            )
            return run_url
        else:
            print(
                "Failed to trigger deployment workflow. Check your GitHub CLI installation and permissions."
            )
            return None


class GithubActionsPromoteWorkflow(PromoteWorkflow):
    """Implements the PromoteWorkflow interface using GitHub Actions."""

    def __init__(self, workflow_file: str = "promote.yml"):
        """
        Initialize the GitHub Actions promote workflow.

        Args:
            workflow_file: The workflow file name (default: promote.yml)
        """
        self.workflow_file = workflow_file
        self.command_executor = CommandExecutor()
        self.git_service = GitService(self.command_executor)
        self.workflow_service = GitHubWorkflowService(
            self.command_executor, self.git_service
        )

    def run(self, flows_to_deploy: List[str], source_env: Optional[str] = None, target_env: Optional[str] = None, ref: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Run the promotion workflow for the specified flows using GitHub Actions.

        Args:
            flows_to_deploy: List of flow names to promote
            source_env: Source environment (required)
            target_env: Target environment (required)
            ref: The git ref (branch/tag) for the workflow (required)
            **kwargs: Additional workflow parameters (for future extensibility)

        Returns:
            Optional[str]: URL of the workflow run if successful, None otherwise
        """
        # Validate required parameters
        if not source_env or not target_env or not ref:
            raise ValueError("source_env, target_env, and ref are required parameters")

        # Convert list to comma-separated string for GitHub Actions input
        flows_str = ",".join(flows_to_deploy)

        # Prepare workflow inputs
        workflow_inputs = {
            "flows-to-deploy": flows_str,
            "source-env": source_env,
            "target-env": target_env,
        }

        # Trigger the workflow
        run_url = self.workflow_service.trigger_workflow(
            self.workflow_file, workflow_inputs, ref
        )

        if run_url:
            print(
                f"Promotion workflow triggered successfully. You can monitor it at: {run_url}"
            )
            return run_url
        else:
            print(
                "Failed to trigger promotion workflow. Check your GitHub CLI installation and permissions."
            )
            return None
