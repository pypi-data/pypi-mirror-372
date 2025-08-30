import os
import sys
import traceback
from pprint import pp
from typing import List, Optional, TYPE_CHECKING
from urllib.parse import urljoin

import requests

from acme_portal_sdk.deployment_finder import DeploymentDetails, DeploymentFinder

if TYPE_CHECKING:
    from acme_portal_sdk.flow_finder import FlowDetails


class AirflowDeploymentFinder(DeploymentFinder):
    """Finds Airflow DAGs in a given context.

    Connects to Airflow's REST API to discover and retrieve information about existing DAGs in the Airflow backend.
    """

    def __init__(
        self,
        airflow_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize the AirflowDeploymentFinder and verify Airflow credentials.

        Args:
            airflow_url: Base URL for Airflow webserver (e.g., http://localhost:8080)
            username: Username for Airflow basic auth
            password: Password for Airflow basic auth
        """
        self.airflow_url = airflow_url or os.environ.get("AIRFLOW_URL")
        self.username = username or os.environ.get("AIRFLOW_USERNAME")
        self.password = password or os.environ.get("AIRFLOW_PASSWORD")
        self.credentials_verified = False

        if not self.airflow_url:
            print(
                "Warning: AIRFLOW_URL not set. Set it to your Airflow webserver URL (e.g., http://localhost:8080)"
            )
            return

        try:
            # Test connection to Airflow API
            response = self._make_request("/api/v1/dags", params={"limit": 1})
            if response.status_code == 200:
                self.credentials_verified = True
                print("Airflow authentication verified successfully.")
            else:
                print(f"Error connecting to Airflow: HTTP {response.status_code}")
        except ImportError:
            print("Error: requests package not installed or not found")
        except Exception as e:
            print(f"Error connecting to Airflow: {str(e)}")
            traceback.print_exc(file=sys.stderr)

    def _make_request(
        self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None
    ) -> requests.Response:
        """Make authenticated request to Airflow API."""
        url = urljoin(self.airflow_url, endpoint)
        auth = (
            (self.username, self.password) if self.username and self.password else None
        )

        response = requests.request(
            method=method,
            url=url,
            auth=auth,
            params=params,
            json=data,
            headers={"Content-Type": "application/json"},
        )
        return response

    def _get_dag_url(self, dag_id: str) -> str:
        """Construct the URL for a given DAG ID."""
        if not self.airflow_url:
            return ""
        return urljoin(self.airflow_url, f"/dags/{dag_id}/grid")

    def get_deployments(
        self,
        deployments_to_fetch: Optional[List[DeploymentDetails]] = None,
        flows_to_fetch: Optional[List["FlowDetails"]] = None
    ) -> List[DeploymentDetails]:
        """Connect to Airflow and get DAG information.
        
        Args:
            deployments_to_fetch: Optional list of specific deployments to re-fetch
            flows_to_fetch: Optional list of flows to re-fetch deployments for
            
        Returns:
            List of DeploymentDetails objects
        """
        if not self.credentials_verified:
            print("Airflow credentials not verified. Cannot fetch deployments.")
            return []

        try:
            # Get all DAGs
            response = self._make_request("/api/v1/dags")

            if response.status_code != 200:
                print(f"Error fetching DAGs: HTTP {response.status_code}")
                return []

            dags_data = response.json()
            dags = dags_data.get("dags", [])

            result = []
            for dag in dags:
                print(f"Processing DAG: {dag['dag_id']}")

                # Parse DAG ID into components
                dag_id = dag["dag_id"]
                parts = dag_id.split("--") if "--" in dag_id else [dag_id]

                # Extract project, branch, flow name, and env from DAG ID or tags
                if len(parts) >= 4:
                    project_name = parts[0]
                    branch = parts[1]
                    flow_name = parts[-2].replace("-", "_")
                    env = parts[-1]
                else:
                    # Fallback: try to extract from tags or use defaults
                    project_name = (
                        self._extract_tag_value(dag.get("tags", []), "PROJECT")
                        or "unknown"
                    )
                    branch = (
                        self._extract_tag_value(dag.get("tags", []), "BRANCH") or "main"
                    )
                    flow_name = dag_id.replace("-", "_")
                    env = self._extract_tag_value(dag.get("tags", []), "ENV") or "dev"

                # Extract additional metadata from tags
                commit_hash = (
                    self._extract_tag_value(dag.get("tags", []), "COMMIT_HASH") or ""
                )
                package_version = (
                    self._extract_tag_value(dag.get("tags", []), "PACKAGE_VERSION")
                    or ""
                )

                # Construct deployment info
                deploy_info = DeploymentDetails(
                    name=dag_id,
                    project_name=project_name,
                    branch=branch,
                    flow_name=flow_name,
                    env=env,
                    commit_hash=commit_hash,
                    package_version=package_version,
                    tags=dag.get("tags", []),
                    id=dag["dag_id"],  # In Airflow, dag_id is the unique identifier
                    created_at=dag.get("created_at", ""),
                    updated_at=dag.get("last_parsed_time", ""),
                    flow_id=dag["dag_id"],  # Same as ID for Airflow
                    url=self._get_dag_url(dag["dag_id"]),
                    child_attributes={
                        "is_active": dag.get("is_active", False),
                        "is_paused": dag.get("is_paused", True),
                        "schedule_interval": dag.get("schedule_interval"),
                        "catchup": dag.get("catchup", False),
                        "max_active_runs": dag.get("max_active_runs", 1),
                        "fileloc": dag.get("fileloc", ""),
                        "owner": dag.get("owners", []),
                    },
                )

                # Filter based on selective parameters
                should_include = True
                
                # If no selective parameters provided, include all
                if deployments_to_fetch is None and flows_to_fetch is None:
                    should_include = True
                else:
                    should_include = False
                    
                    # Check if this deployment should be included based on deployments_to_fetch
                    if deployments_to_fetch is not None:
                        deployment_ids_to_fetch = {d.id for d in deployments_to_fetch}
                        if deploy_info.id in deployment_ids_to_fetch:
                            should_include = True
                    
                    # Check if this deployment should be included based on flows_to_fetch
                    if flows_to_fetch is not None and not should_include:
                        flow_names_to_fetch = {f.name for f in flows_to_fetch}
                        if deploy_info.flow_name in flow_names_to_fetch:
                            should_include = True

                if should_include:
                    result.append(deploy_info)
                    print(
                        f"Added DAG: {deploy_info.project_name}/{flow_name} ({deploy_info.branch}/{deploy_info.env})"
                    )

            return result
        except ImportError:
            print("Error: requests package not installed or not found")
            raise
        except Exception as e:
            print(f"Error getting DAGs: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            raise

    def _extract_tag_value(self, tags: List[str], tag_prefix: str) -> Optional[str]:
        """Extract value from tags with format 'PREFIX=value'."""
        for tag in tags:
            if tag.startswith(f"{tag_prefix}="):
                return tag.split("=", 1)[1]
        return None


if __name__ == "__main__":
    finder = AirflowDeploymentFinder()
    deployments = finder.get_deployments()
    pp(deployments)
