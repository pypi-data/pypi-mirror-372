
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Tuple

class ResourceType(Enum):
    """Enumeration for different types of resources."""
    COMPUTE = "compute"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    ENERGY = "energy"

class AuctionStatus(Enum):
    """Enumeration for the status of an auction."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Resource:
    """
    Represents an IoT resource in the simulation.

    Attributes:
        id: Unique identifier for the resource.
        type: The type of the resource (e.g., COMPUTE, STORAGE).
        capacity: The total capacity of the resource.
        cost_per_unit: The cost per unit of capacity.
        location: The (x, y) coordinates of the resource.
        availability: The availability of the resource (0-1).
        reliability: The reliability of the resource (0-1).
        energy_efficiency: The energy efficiency of the resource (0-1).
        owner_id: The ID of the resource owner.
    """
    id: str
    type: ResourceType
    capacity: float
    cost_per_unit: float
    location: Tuple[float, float]
    availability: float
    reliability: float
    energy_efficiency: float
    owner_id: str

@dataclass
class Request:
    """
    Represents a resource request from an IoT device or application.

    Attributes:
        id: Unique identifier for the request.
        requester_id: The ID of the requester.
        resource_type: The type of resource being requested.
        amount: The amount of resource being requested.
        max_price: The maximum price the requester is willing to pay.
        deadline: The deadline for the request to be fulfilled.
        priority: The priority of the request (1-10).
        location: The (x, y) coordinates of the requester.
        qos_requirements: A dictionary of QoS requirements.
    """
    id: str
    requester_id: str
    resource_type: ResourceType
    amount: float
    max_price: float
    deadline: float
    priority: int
    location: Tuple[float, float]
    qos_requirements: Dict[str, float]

@dataclass
class Bid:
    """
    Represents a bid in the auction.

    Attributes:
        id: Unique identifier for the bid.
        resource_id: The ID of the resource being bid on.
        request_id: The ID of the request that generated the bid.
        price: The price of the bid.
        amount: The amount of resource being bid for.
        utility_score: The calculated utility score of the bid.
    """
    id: str
    resource_id: str
    request_id: str
    price: float
    amount: float
    utility_score: float

class BaseAuctionMechanism:
    """
    Base class for all auction mechanisms.

    This class provides a common interface for running auctions and calculating
    performance metrics. All new auction mechanisms should inherit from this
    class and implement the `run_auction` method.
    """

    def __init__(self, name: str):
        """
        Initializes the auction mechanism.

        Args:
            name: The name of the auction mechanism.
        """
        self.name = name
        self.results = []

    def run_auction(self, resources: List[Resource], requests: List[Request]) -> Dict:
        """
        Runs the auction.

        This method should be implemented by all subclasses.

        Args:
            resources: A list of available resources.
            requests: A list of resource requests.

        Returns:
            A dictionary containing the results of the auction.
        """
        raise NotImplementedError

    def calculate_metrics(self, allocation_result: Dict) -> Dict:
        """
        Calculates performance metrics for the auction.

        Args:
            allocation_result: The result of the auction.

        Returns:
            A dictionary of performance metrics.
        """
        from . import utils

        metrics = {
            'allocation_efficiency': utils.calculate_allocation_efficiency(allocation_result),
            'revenue': utils.calculate_total_revenue(allocation_result),
            'satisfaction_rate': utils.calculate_satisfaction_rate(allocation_result),
            'resource_utilization': utils.calculate_resource_utilization(allocation_result),
            'execution_time': allocation_result.get('execution_time', 0),
            'communication_overhead': allocation_result.get('communication_overhead', 0),
            'fairness_index': utils.calculate_fairness_index(allocation_result)
        }
        return metrics
