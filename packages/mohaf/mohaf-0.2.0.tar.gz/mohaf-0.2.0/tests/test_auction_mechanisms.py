
from mohaf.auction_mechanisms import (
    MOHAFAuction,
    FirstPriceAuction,
    VickreyAuction,
    HungarianAlgorithm,
    GreedyAuction,
    RandomAuction,
)

def test_mohaf_creation():
    """Tests if a MOHAFAuction object can be created."""
    auction = MOHAFAuction()
    assert auction.name == "MOHAF"

def test_first_price_creation():
    """Tests if a FirstPriceAuction object can be created."""
    auction = FirstPriceAuction()
    assert auction.name == "First-Price Auction"

def test_vickrey_creation():
    """Tests if a VickreyAuction object can be created."""
    auction = VickreyAuction()
    assert auction.name == "Vickrey Auction"

def test_hungarian_creation():
    """Tests if a HungarianAlgorithm object can be created."""
    auction = HungarianAlgorithm()
    assert auction.name == "Hungarian Algorithm"

def test_greedy_creation():
    """Tests if a GreedyAuction object can be created."""
    auction = GreedyAuction()
    assert auction.name == "Greedy Auction"


def test_random_creation():
    """Tests if a RandomAuction object can be created."""
    auction = RandomAuction()
    assert auction.name == "Random Auction"
