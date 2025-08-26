
import random
import time
from typing import List, Tuple

from .core import Resource, Request, ResourceType

def generate_synthetic_scenario(
    n_resources: int = 50,
    n_requests: int = 30,
    scenario_type: str = "balanced",
) -> Tuple[List[Resource], List[Request]]:
    """
    Generates a synthetic IoT scenario with resources and requests.

    Args:
        n_resources: The number of resources to generate.
        n_requests: The number of requests to generate.
        scenario_type: The type of scenario to generate (e.g., 'balanced',
            'high_demand', 'low_resource').

    Returns:
        A tuple containing a list of resources and a list of requests.
    """
    print(f"Generating {scenario_type} scenario: {n_resources} resources, {n_requests} requests")

    resources = []
    requests = []

    # Generate resources
    resource_types = list(ResourceType)

    for i in range(n_resources):
        resource_type = random.choice(resource_types)

        # Scenario-specific parameters
        if scenario_type == "high_demand":
            capacity = random.uniform(10, 50)
            cost = random.uniform(0.5, 2.0)
        elif scenario_type == "low_resource":
            capacity = random.uniform(5, 20)
            cost = random.uniform(1.0, 3.0)
        else:  # balanced
            capacity = random.uniform(20, 100)
            cost = random.uniform(0.3, 1.5)

        resource = Resource(
            id=f"resource_{i}",
            type=resource_type,
            capacity=capacity,
            cost_per_unit=cost,
            location=(random.uniform(-50, 50), random.uniform(-50, 50)),
            availability=random.uniform(0.7, 1.0),
            reliability=random.uniform(0.6, 0.95),
            energy_efficiency=random.uniform(0.5, 0.9),
            owner_id=f"owner_{i % (n_resources // 3)}",
        )
        resources.append(resource)

    # Generate requests
    for i in range(n_requests):
        resource_type = random.choice(resource_types)

        if scenario_type == "high_demand":
            amount = random.uniform(30, 80)
            max_price = random.uniform(50, 150)
        elif scenario_type == "low_resource":
            amount = random.uniform(10, 30)
            max_price = random.uniform(20, 60)
        else:  # balanced
            amount = random.uniform(15, 60)
            max_price = random.uniform(30, 100)

        request = Request(
            id=f"request_{i}",
            requester_id=f"requester_{i}",
            resource_type=resource_type,
            amount=amount,
            max_price=max_price,
            deadline=time.time() + random.uniform(300, 1800),
            priority=random.randint(1, 10),
            location=(random.uniform(-50, 50), random.uniform(-50, 50)),
            qos_requirements={
                'min_reliability': random.uniform(0.5, 0.9),
                'max_latency': random.uniform(10, 100),
                'min_availability': random.uniform(0.6, 0.95),
            },
        )
        requests.append(request)

    return resources, requests
