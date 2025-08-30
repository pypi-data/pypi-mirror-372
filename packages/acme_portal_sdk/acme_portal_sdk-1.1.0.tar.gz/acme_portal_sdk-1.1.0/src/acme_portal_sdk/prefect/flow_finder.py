import ast
import os
import sys
import traceback
from dataclasses import dataclass
from pprint import pp
from typing import Dict, List, Optional

from acme_portal_sdk.flow_finder import FlowDetails, FlowFinder

PrefectFlowDetails = FlowDetails


@dataclass
class PrefectFlowAttributes:
    """Dataclass to capture Prefect-specific attributes stored in child_attributes.
    
    This dataclass represents the implementation-specific metadata that Prefect
    flow finder collects about discovered flows. These attributes provide detailed
    information about how the flow is implemented in Python code.
    
    Attributes:
        obj_type: Type of object defining the flow ("function" or "method")
        obj_name: Name of the function or method that defines the flow
        obj_parent_type: Type of container for the flow object ("module" or "class")
        obj_parent: Name of the module or class containing the flow
        module: Python module name where the flow is defined
        import_path: Full Python import path to the source file
    """
    obj_type: str
    obj_name: str
    obj_parent_type: str
    obj_parent: str
    module: str
    import_path: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert the dataclass to a dictionary for use in child_attributes."""
        return {
            "obj_type": self.obj_type,
            "obj_name": self.obj_name,
            "obj_parent_type": self.obj_parent_type,
            "obj_parent": self.obj_parent,
            "module": self.module,
            "import_path": self.import_path,
        }


class PrefectFlowFinder(FlowFinder):
    """Scans Python code directories to identify Prefect flows by analyzing decorators, extracting metadata and organizing found flows into flat list."""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    class _FlowVisitor(ast.NodeVisitor):
        """AST visitor to find Prefect flow decorators in Python code."""

        def __init__(self, module: str):
            self.flows = {}
            self.current_class = None
            self.current_function = None
            self.module = module

        def visit_ClassDef(self, node):
            old_class = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = old_class

        def visit_FunctionDef(self, node):
            """Visit a function definition node."""
            self.current_function = node.name
            # Look for decorators that might be flows
            for decorator in node.decorator_list:
                if self._is_flow_decorator(decorator):
                    # Found a flow decorator
                    # Extract keyword arguments from decorator
                    kwargs = self._extract_decorator_kwargs(decorator)
                    flow_name = kwargs.get("name", self.current_function)
                    display_name = flow_name.replace("-", "_")

                    description = kwargs.get("description", "") or ast.get_docstring(
                        node
                    )
                    # Create a unique ID based on the function name and location
                    flow_key = f"{flow_name}_{id(node)}"

                    # Create child_attributes with implementation-specific details
                    prefect_attrs = PrefectFlowAttributes(
                        obj_type="function",
                        obj_name=self.current_function,
                        obj_parent_type="module",
                        obj_parent=self.module,
                        module=self.module,
                        import_path=""  # Will be set later in _scan_file
                    )

                    if self.current_class:
                        prefect_attrs.obj_type = "method"
                        prefect_attrs.obj_parent = self.current_class
                        prefect_attrs.obj_parent_type = "class"

                    self.flows[flow_key] = {
                        "name": display_name,
                        "original_name": flow_name,
                        "description": description,
                        "id": flow_key,
                        "child_attributes": prefect_attrs,  # Store the dataclass directly
                    }

                    # Debug output to help troubleshoot
                    print(f"Found flow: {display_name} (from function {flow_name})")

            self.generic_visit(node)
            self.current_function = None

        def _is_flow_decorator(self, decorator):
            """Check if a decorator is a flow decorator."""
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "flow"
            ):
                return True

            # Also check for prefect.flow or from prefect import flow
            if isinstance(decorator, ast.Call) and isinstance(
                decorator.func, ast.Attribute
            ):
                if decorator.func.attr == "flow":
                    return True

            return False

        def _extract_decorator_kwargs(self, decorator):
            """Extract keyword arguments from a decorator."""
            kwargs = {}
            if isinstance(decorator, ast.Call):
                for keyword in decorator.keywords:
                    if isinstance(keyword.value, ast.Constant):
                        kwargs[keyword.arg] = keyword.value.value
                    elif isinstance(keyword.value, ast.Str):  # For Python < 3.8
                        kwargs[keyword.arg] = keyword.value.s
            return kwargs

    def _scan_file(self, file_path: str) -> Dict[str, FlowDetails]:
        """Scan a single Python file for flows."""
        flows = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the file
            tree = ast.parse(content)
            module = os.path.splitext(os.path.basename(file_path))[0]
            visitor = self._FlowVisitor(module)
            visitor.visit(tree)

            # Process found flows
            for key, flow_data in visitor.flows.items():
                # Add file information
                flow_data["source_path"] = file_path
                flow_data["source_relative"] = os.path.relpath(
                    file_path, start=self.root_dir
                )
                flow_data["grouping"] = flow_data["source_relative"].split(os.sep)[
                    :-1
                ]  # Grouping by directory structure
                package_name = os.path.basename(self.root_dir)
                import_path = (
                    f"{package_name}.{flow_data['source_relative'].replace(os.sep, '.').replace('.py', '')}"
                )
                
                # Update the import_path in the PrefectFlowAttributes and convert to dict
                prefect_attrs = flow_data["child_attributes"]  # Get the dataclass directly
                prefect_attrs.import_path = import_path
                flow_data["child_attributes"] = prefect_attrs.to_dict()
                
                flow_data = FlowDetails(**flow_data)
                # Add the flow to the results
                flows[key] = flow_data

                print(f"Added flow to results: {flow_data.name}")

        except Exception as e:
            print(f"Error scanning {file_path}: {str(e)}")
            traceback.print_exc(file=sys.stderr)

        return flows

    def _scan_directory(self, root_dir: str) -> Dict[str, FlowDetails]:
        """Recursively scan a directory for Python files with flows."""
        all_flows = {}

        print(f"Scanning directory: {root_dir}")

        try:
            # todo: https://stackoverflow.com/questions/25229592/python-how-to-implement-something-like-gitignore-behavior
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        print(f"Examining file: {file_path}")
                        flows = self._scan_file(file_path)
                        if flows:
                            print(f"Found {len(flows)} flows in {file_path}")
                        all_flows.update(flows)
        except Exception as e:
            print(f"Error walking directory {root_dir}: {str(e)}")
            traceback.print_exc(file=sys.stderr)

        return all_flows

    def find_flows(
        self, 
        flows_to_fetch: Optional[List[FlowDetails]] = None,
        flow_groups: Optional[List[str]] = None
    ) -> List[FlowDetails]:
        """Find flows, optionally re-fetching specific flows or groups.
        
        Args:
            flows_to_fetch: Optional list of flows to selectively re-fetch data for
            flow_groups: Optional list of flow group names to selectively re-fetch
            
        Returns:
            List of FlowDetails objects
        """
        all_flows = self._scan_directory(self.root_dir)
        
        # If no selective parameters provided, return all flows
        if flows_to_fetch is None and flow_groups is None:
            return list(all_flows.values())
            
        result = []
        
        # Handle selective flow re-fetching
        if flows_to_fetch is not None:
            flows_to_fetch_keys = {(flow.name, flow.source_relative) for flow in flows_to_fetch}
            for flow_id, flow in all_flows.items():
                if (flow.name, flow.source_relative) in flows_to_fetch_keys:
                    result.append(flow)
        
        # Handle flow groups re-fetching
        if flow_groups is not None:
            for flow in all_flows.values():
                # Check if any of the flow's grouping elements match the requested groups
                if any(group in flow_groups for group in flow.grouping):
                    # Avoid duplicates if flow was already added from flows_to_fetch
                    if flows_to_fetch is None or (flow.name, flow.source_relative) not in {(f.name, f.source_relative) for f in flows_to_fetch}:
                        result.append(flow)
        
        return result


if __name__ == "__main__":
    a = PrefectFlowFinder("examples/flows")
    pp(a.find_flows())
