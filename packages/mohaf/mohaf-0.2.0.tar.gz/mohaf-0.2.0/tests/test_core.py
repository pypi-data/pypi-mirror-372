
from mohaf.core import Resource, Request, ResourceType

def test_resource_creation():
    """Tests if a Resource object can be created."""
    resource = Resource(
        id="res1",
        type=ResourceType.COMPUTE,
        capacity=100.0,
        cost_per_unit=0.5,
        location=(10, 20),
        availability=0.99,
        reliability=0.95,
        energy_efficiency=0.9,
        owner_id="owner1",
    )
    assert resource.id == "res1"
    assert resource.type == ResourceType.COMPUTE

def test_request_creation():
    """Tests if a Request object can be created."""
    request = Request(
        id="req1",
        requester_id="user1",
        resource_type=ResourceType.COMPUTE,
        amount=50.0,
        max_price=1.0,
        deadline=12345.67,
        priority=5,
        location=(15, 25),
        qos_requirements={},
    )
    assert request.id == "req1"
    assert request.amount == 50.0
