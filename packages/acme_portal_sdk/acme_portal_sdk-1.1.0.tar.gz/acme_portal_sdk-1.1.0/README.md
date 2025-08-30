# acme-portal-sdk

> **Important:** This SDK is currently in alpha and primarily for demonstration purposes. APIs may still change frequently.

## Overview

**acme-portal-sdk** is a Python SDK that provides data and actions for the `acme-portal` VSCode [extension](https://github.com/blackwhitehere/acme-portal). It standardizes the deployment workflow for Python applications that implement "flows" (Jobs/DAGs/Workflows) while allowing full customization of the underlying implementation.

[AI wiki](https://deepwiki.com/blackwhitehere/acme-portal-sdk/)

### Main Idea

Rather than embedding pre-defined deployment logic in the VSCode extension, the SDK allows you to define custom sources of data and behavior. The extension serves as a UI layer to your SDK implementations, providing a consistent interface for:

- **Discovering flows** in your codebase
- **Managing deployments** across environments 
- **Promoting deployments** between environments (dev → staging → prod)

The SDK defines abstract interfaces that you implement according to your project's needs, whether using Prefect, Airflow, GitHub Actions, or custom deployment systems.

## Quick Start

To set up your project with acme-portal-sdk, create a `.acme_portal_sdk` directory in your project root with these files:

### 1. Install the SDK

```bash
pip install acme_portal_sdk
```

### 2. Create SDK Configuration Files

```bash
mkdir .acme_portal_sdk
```

#### `.acme_portal_sdk/flow_finder.py`
```python
from acme_portal_sdk.flow_finder import FlowFinder, FlowDetails
from pathlib import Path
from typing import List
import ast
import os

class MyCustomFlowFinder(FlowFinder):
    """Custom implementation to find flows in your codebase."""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
    
    def find_flows(self) -> List[FlowDetails]:
        """Find flows by scanning Python files for flow decorators."""
        flows = []
        
        for py_file in self.root_dir.rglob("*.py"):
            if py_file.is_file():
                try:
                    with open(py_file, 'r') as f:
                        tree = ast.parse(f.read())
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Look for @flow decorator or similar patterns
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Name) and decorator.id == 'flow':
                                    flows.append(FlowDetails(
                                        name=node.name,
                                        original_name=node.name,
                                        description=ast.get_docstring(node) or "",
                                        obj_type="function",
                                        obj_name=node.name,
                                        obj_parent_type="module",
                                        obj_parent=py_file.stem,
                                        id=f"{py_file.stem}.{node.name}",
                                        module=py_file.stem,
                                        source_path=str(py_file),
                                        source_relative=str(py_file.relative_to(self.root_dir)),
                                        import_path=f"{py_file.stem}",
                                        grouping=[py_file.parent.name]
                                    ))
                except Exception:
                    continue
        
        return flows

# Create an instance to find flows in your project
project_root = Path(__file__).parent.parent
flow_finder = MyCustomFlowFinder(
    root_dir=str(project_root / "src" / "your_project_name")
)
```

#### `.acme_portal_sdk/deployment_finder.py`
```python
from acme_portal_sdk.deployment_finder import DeploymentFinder, DeploymentDetails
from typing import List
import requests

class MyCustomDeploymentFinder(DeploymentFinder):
    """Custom implementation to find existing deployments."""
    
    def __init__(self, api_base_url: str = "https://your-deployment-api.com"):
        self.api_base_url = api_base_url
    
    def get_deployments(self) -> List[DeploymentDetails]:
        """Fetch deployments from your deployment API."""
        try:
            response = requests.get(f"{self.api_base_url}/deployments")
            response.raise_for_status()
            
            deployments = []
            for data in response.json():
                deployments.append(DeploymentDetails(
                    name=data["name"],
                    project_name=data["project"],
                    branch=data["branch"],
                    flow_name=data["flow_name"],
                    env=data["environment"],
                    commit_hash=data["commit_hash"],
                    package_version=data.get("version", "unknown"),
                    tags=data.get("tags", []),
                    id=data["id"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    flow_id=data["flow_id"],
                    url=data["url"]
                ))
            
            return deployments
        except Exception:
            return []

# Find existing deployments from your API
deployment_finder = MyCustomDeploymentFinder()
```

#### `.acme_portal_sdk/flow_deploy.py`
```python
from acme_portal_sdk.flow_deploy import DeployWorkflow
from typing import Any, Optional
import subprocess

class MyCustomDeployWorkflow(DeployWorkflow):
    """Custom implementation for deploying flows."""
    
    def __init__(self, deploy_script: str = "scripts/deploy.sh"):
        self.deploy_script = deploy_script
    
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Deploy flows using custom deployment script."""
        try:
            flows_to_deploy = kwargs.get("flows_to_deploy", [])
            env = kwargs.get("env", "dev")
            branch_name = kwargs.get("branch_name", "main")
            
            # Build deployment command
            cmd = [
                "bash", self.deploy_script,
                "--flows", ",".join(flows_to_deploy),
                "--env", env,
                "--branch", branch_name
            ]
            
            # Execute deployment
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Return deployment URL if available in output
                return result.stdout.strip()
            else:
                print(f"Deployment failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Deployment error: {e}")
            return None

# Deploy flows using custom script
deploy = MyCustomDeployWorkflow(deploy_script="scripts/deploy.sh")
```

#### `.acme_portal_sdk/deployment_promote.py`
```python
from acme_portal_sdk.deployment_promote import PromoteWorkflow
from typing import Any, Optional
import subprocess

class MyCustomPromoteWorkflow(PromoteWorkflow):
    """Custom implementation for promoting deployments between environments."""
    
    def __init__(self, promote_script: str = "scripts/promote.sh"):
        self.promote_script = promote_script
    
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Promote deployments using custom promotion script."""
        try:
            flows_to_deploy = kwargs.get("flows_to_deploy", [])
            source_env = kwargs.get("source_env", "dev")
            target_env = kwargs.get("target_env", "prod")
            project_name = kwargs.get("project_name", "")
            
            # Build promotion command
            cmd = [
                "bash", self.promote_script,
                "--flows", ",".join(flows_to_deploy),
                "--from", source_env,
                "--to", target_env,
                "--project", project_name
            ]
            
            # Execute promotion
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Return promotion URL if available in output
                return result.stdout.strip()
            else:
                print(f"Promotion failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Promotion error: {e}")
            return None

# Promote deployments using custom script
promote = MyCustomPromoteWorkflow(promote_script="scripts/promote.sh")
```

### 3. Install VSCode Extension

Install the [`acme-portal` VSCode extension](https://github.com/blackwhitehere/acme-portal) to get the UI interface for managing your flows and deployments.

## Documentation

- **[Core Concepts](docs/docs/user/concepts.md)** - Understanding flows, deployments, and environments
- **[User Guides](docs/docs/user/user-guides.md)** - Detailed configuration examples
- **[Features](docs/docs/user/features.md)** - Available functionality and platform support
- **[API Reference](docs/docs/developer/api-reference.md)** - Complete API documentation

### Example Projects

- **[acme-prefect](https://github.com/blackwhitehere/acme-prefect)** - Complete example using Prefect workflows

## Development

For detailed development setup, contribution guidelines, and release notes process, see [CONTRIBUTING.md](CONTRIBUTING.md).