from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FlowDetails:
    """Holds details about a flow.

    Flow (often named Workflow/Job/DAG) is a unit of work in a program.

    Attributes:
        name: Display name, may be a normalized version of the original name
        original_name: Name as defined in the code
        description: Description of the flow
        id: Unique identifier for the flow definition in memory
        source_path: Unambiguous path to the source file from the root of the project
        source_relative: Relative path to the source file from some known root
        line_number: Line number where the flow is defined in the source file
        grouping: Desired grouping of the flow in the context of the project (for navigation)
        child_attributes: Additional attributes specific to implementation (e.g., obj_type, obj_name,
                         obj_parent_type, obj_parent, module, import_path for Prefect). Should not be
                         set by subclasses, but may be set by users to add custom information.
    """

    name: str
    original_name: str
    description: str
    id: str
    source_path: str
    source_relative: str
    line_number: Optional[int] = None
    grouping: List[str] = field(default_factory=list)
    child_attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the FlowDetails to a dictionary suitable for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlowDetails":
        """Create a FlowDetails instance from a dictionary representation."""
        return cls(**data)


class FlowFinder(ABC):
    """Finds flows (units of work/programs) in a given context, with implementations providing specific discovery mechanisms."""

    @abstractmethod
    def find_flows(
        self,
        *,
        flows_to_fetch: Optional[List[FlowDetails]] = None,
        flow_groups: Optional[List[str]] = None,
    ) -> List[FlowDetails]:
        """Method to find flows, to be implemented by subclasses.

        kwargs:
            flows_to_fetch: Optional list of flows to selectively re-fetch data for
            flow_groups: Optional list of flow group names to selectively re-fetch

        Returns:
            List of FlowDetails objects
        """
        pass

    def __call__(
        self,
        *,
        flows_to_fetch: Optional[List[dict]] = None,
        flow_groups: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Passthrough method for find_flows call that is operating on JSON (serializable) types"""
        return [
            x.to_dict()
            for x in self.find_flows(
                flows_to_fetch=[FlowDetails.from_dict(x) for x in flows_to_fetch]
                if flows_to_fetch is not None
                else flows_to_fetch,
                flow_groups=flow_groups,
            )
        ]
