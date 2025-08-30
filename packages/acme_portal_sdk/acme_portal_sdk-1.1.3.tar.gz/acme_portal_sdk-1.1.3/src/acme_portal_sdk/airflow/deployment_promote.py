import os
import sys
import traceback
from typing import List, Optional

import requests
from urllib.parse import urljoin

from acme_portal_sdk.deployment_promote import DeploymentPromote


class AirflowDeploymentPromote(DeploymentPromote):
    """Responsible for promoting DAGs between different Airflow environments."""

    def __init__(
        self,
        source_airflow_url: Optional[str] = None,
        target_airflow_url: Optional[str] = None,
        source_username: Optional[str] = None,
        source_password: Optional[str] = None,
        target_username: Optional[str] = None,
        target_password: Optional[str] = None,
    ):
        """Initialize the AirflowDeploymentPromote.

        Args:
            source_airflow_url: Base URL for source Airflow webserver
            target_airflow_url: Base URL for target Airflow webserver
            source_username: Username for source Airflow basic auth
            source_password: Password for source Airflow basic auth
            target_username: Username for target Airflow basic auth
            target_password: Password for target Airflow basic auth
        """
        self.source_airflow_url = source_airflow_url or os.environ.get(
            "AIRFLOW_SOURCE_URL"
        )
        self.target_airflow_url = target_airflow_url or os.environ.get(
            "AIRFLOW_TARGET_URL"
        )
        self.source_username = source_username or os.environ.get(
            "AIRFLOW_SOURCE_USERNAME"
        )
        self.source_password = source_password or os.environ.get(
            "AIRFLOW_SOURCE_PASSWORD"
        )
        self.target_username = target_username or os.environ.get(
            "AIRFLOW_TARGET_USERNAME"
        )
        self.target_password = target_password or os.environ.get(
            "AIRFLOW_TARGET_PASSWORD"
        )

        if not self.source_airflow_url:
            raise ValueError(
                "AIRFLOW_SOURCE_URL not set. Set it to your source Airflow webserver URL"
            )
        if not self.target_airflow_url:
            raise ValueError(
                "AIRFLOW_TARGET_URL not set. Set it to your target Airflow webserver URL"
            )

    def _make_request(
        self,
        base_url: str,
        username: str,
        password: str,
        endpoint: str,
        method: str = "GET",
        params: dict = None,
        data: dict = None,
    ) -> requests.Response:
        """Make authenticated request to Airflow API."""
        url = urljoin(base_url, endpoint)
        auth = (username, password) if username and password else None

        response = requests.request(
            method=method,
            url=url,
            auth=auth,
            params=params,
            json=data,
            headers={"Content-Type": "application/json"},
        )
        return response

    def promote(
        self,
        project_name: str,
        branch_name: str,
        source_env: str,
        target_env: str,
        flows_to_deploy: List[str],
    ) -> None:
        """Promote DAGs from one Airflow environment to another.

        Args:
            project_name: Name of the project
            branch_name: Name of the branch
            source_env: Source environment
            target_env: Target environment
            flows_to_deploy: List of flow names to promote
        """
        try:
            for flow_name in flows_to_deploy:
                # Construct DAG IDs for source and target environments
                source_dag_id = (
                    f"{project_name}--{branch_name}--{flow_name}--{source_env}"
                )
                target_dag_id = (
                    f"{project_name}--{branch_name}--{flow_name}--{target_env}"
                )

                print(f"Promoting DAG from {source_dag_id} to {target_dag_id}")

                # Get source DAG configuration
                source_dag = self._get_dag_config(
                    self.source_airflow_url,
                    self.source_username,
                    self.source_password,
                    source_dag_id,
                )

                if not source_dag:
                    print(f"Source DAG {source_dag_id} not found. Skipping.")
                    continue

                # Check if target DAG exists
                target_dag = self._get_dag_config(
                    self.target_airflow_url,
                    self.target_username,
                    self.target_password,
                    target_dag_id,
                )

                if not target_dag:
                    print(
                        f"Target DAG {target_dag_id} not found. Cannot promote - DAG file must exist in target environment."
                    )
                    continue

                # Update target DAG configuration based on source
                self._update_dag_config(
                    self.target_airflow_url,
                    self.target_username,
                    self.target_password,
                    target_dag_id,
                    source_dag,
                )

                print(
                    f"Successfully promoted {flow_name} from {source_env} to {target_env}"
                )

        except Exception as e:
            print(f"Error promoting DAGs: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            raise

    def _get_dag_config(
        self, base_url: str, username: str, password: str, dag_id: str
    ) -> Optional[dict]:
        """Get DAG configuration from Airflow."""
        try:
            response = self._make_request(
                base_url, username, password, f"/api/v1/dags/{dag_id}"
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                print(f"Error fetching DAG {dag_id}: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching DAG configuration for {dag_id}: {str(e)}")
            return None

    def _update_dag_config(
        self,
        base_url: str,
        username: str,
        password: str,
        dag_id: str,
        source_config: dict,
    ) -> None:
        """Update target DAG configuration based on source."""
        try:
            # Extract relevant configuration from source
            update_data = {}

            # Copy pause state (you might want to always start as paused in prod)
            if "is_paused" in source_config:
                update_data["is_paused"] = source_config["is_paused"]

            # Update the target DAG
            response = self._make_request(
                base_url,
                username,
                password,
                f"/api/v1/dags/{dag_id}",
                method="PATCH",
                data=update_data,
            )

            if response.status_code == 200:
                print(f"Successfully updated target DAG {dag_id}")
            else:
                print(
                    f"Error updating target DAG {dag_id}: HTTP {response.status_code}"
                )
                print(response.text)

        except Exception as e:
            print(f"Error updating DAG configuration for {dag_id}: {str(e)}")
            traceback.print_exc(file=sys.stderr)
