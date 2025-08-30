import os
import sys
import traceback
from typing import Optional

import requests
from urllib.parse import urljoin

from acme_portal_sdk.flow_deploy import DeployInfo, FlowDeployer


class AirflowFlowDeployer(FlowDeployer):
    """Deploys flows to Airflow by updating DAG configuration or triggering DAG creation."""

    def __init__(
        self,
        airflow_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize the AirflowFlowDeployer.

        Args:
            airflow_url: Base URL for Airflow webserver (e.g., http://localhost:8080)
            username: Username for Airflow basic auth
            password: Password for Airflow basic auth
        """
        self.airflow_url = airflow_url or os.environ.get("AIRFLOW_URL")
        self.username = username or os.environ.get("AIRFLOW_USERNAME")
        self.password = password or os.environ.get("AIRFLOW_PASSWORD")

        if not self.airflow_url:
            raise ValueError(
                "AIRFLOW_URL not set. Set it to your Airflow webserver URL (e.g., http://localhost:8080)"
            )

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

    def deploy(self, flow_deploy_info: DeployInfo) -> None:
        """Deploy a flow to Airflow.

        WARNING: This implementation is incomplete and Airflow deployment steps 
        vary by specific setup. In production environments, you may need to:
        - Copy DAG files to the DAGs folder
        - Use DAG synchronization mechanisms (Git-sync, S3, etc.)
        - Implement custom deployment logic for your Airflow setup
        - Handle DAG dependencies and requirements

        For Airflow, deployment typically means:
        1. Ensuring the DAG file is in the DAGs folder
        2. Optionally triggering a DAG refresh
        3. Updating DAG configuration (pause/unpause, etc.)

        Args:
            flow_deploy_info: Configuration for the deployment
        """
        try:
            dag_id = flow_deploy_info.name

            print(f"Deploying DAG: {dag_id}")

            # Check if DAG exists
            response = self._make_request(f"/api/v1/dags/{dag_id}")

            if response.status_code == 404:
                print(
                    f"DAG {dag_id} not found in Airflow. Make sure the DAG file is in the DAGs folder."
                )
                # In a real implementation, you might want to copy the DAG file to the DAGs folder
                # or trigger a DAG folder refresh
                return
            elif response.status_code != 200:
                print(f"Error checking DAG {dag_id}: HTTP {response.status_code}")
                return

            # Update DAG configuration
            dag_update_data = {}

            # Set pause state
            if flow_deploy_info.paused is not None:
                dag_update_data["is_paused"] = flow_deploy_info.paused

            # Update DAG if there are changes
            if dag_update_data:
                response = self._make_request(
                    f"/api/v1/dags/{dag_id}", method="PATCH", data=dag_update_data
                )

                if response.status_code == 200:
                    print(f"Successfully updated DAG {dag_id}")
                else:
                    print(f"Error updating DAG {dag_id}: HTTP {response.status_code}")
                    print(response.text)

            # Optionally trigger a DAG run if specified
            if (
                hasattr(flow_deploy_info, "trigger_run")
                and flow_deploy_info.trigger_run
            ):
                self._trigger_dag_run(dag_id, flow_deploy_info.parameters or {})

            print(f"Deployment of DAG {dag_id} completed")

        except Exception as e:
            print(f"Error deploying DAG {flow_deploy_info.name}: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            raise

    def _trigger_dag_run(self, dag_id: str, parameters: dict) -> None:
        """Trigger a DAG run."""
        try:
            run_data = {"conf": parameters}

            response = self._make_request(
                f"/api/v1/dags/{dag_id}/dagRuns", method="POST", data=run_data
            )

            if response.status_code == 200:
                run_info = response.json()
                print(
                    f"Successfully triggered DAG run for {dag_id}: {run_info.get('dag_run_id')}"
                )
            else:
                print(
                    f"Error triggering DAG run for {dag_id}: HTTP {response.status_code}"
                )
                print(response.text)

        except Exception as e:
            print(f"Error triggering DAG run for {dag_id}: {str(e)}")
            traceback.print_exc(file=sys.stderr)
