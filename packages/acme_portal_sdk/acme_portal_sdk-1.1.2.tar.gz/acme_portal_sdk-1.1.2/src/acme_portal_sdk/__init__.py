import logging

from dotenv import load_dotenv

# isort: off
from ._main import main  # noqa: F401
from .deployment_finder import DeploymentDetails  # noqa: F401
from .deployment_finder import DeploymentFinder  # noqa: F401
from .deployment_promote import DeploymentPromote  # noqa: F401
from .deployment_promote import PromoteWorkflow  # noqa: F401
from .flow_deploy import DeployWorkflow  # noqa: F401
from .flow_deploy import DeployInfo, DeployInfoPrep, FlowDeployer  # noqa: F401
from .flow_finder import FlowDetails, FlowFinder  # noqa: F401

load_dotenv()

PROTOCOL_VERSION = 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(pathname)s | %(name)s | func: %(funcName)s:%(lineno)s | %(levelname)s | %(message)s",
)
