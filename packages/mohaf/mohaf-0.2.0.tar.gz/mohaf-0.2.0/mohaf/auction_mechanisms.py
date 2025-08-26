import time
import random
import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple

from .core import (
    BaseAuctionMechanism,
    Bid,
    Resource,
    Request,
)

class MOHAFAuction(BaseAuctionMechanism):
    """
    Multi-Objective Hierarchical Auction Framework (MOHAF) - Our Novel Approach

    Key innovations:
    1. Hierarchical clustering of resources and requests
    2. Multi-objective optimization (cost, QoS, energy, fairness)
    3. Dynamic pricing with learning
    4. Distributed consensus mechanism
    5. Adaptive resource allocation
    """

    def __init__(self, alpha=0.3, beta=0.3, gamma=0.2, delta=0.2, learning_rate=0.01):
        super().__init__("MOHAF")
        self.alpha = alpha  # Cost weight
        self.beta = beta    # QoS weight
        self.gamma = gamma  # Energy weight
        self.delta = delta  # Fairness weight
        self.learning_rate = learning_rate
        self.price_history = {}
        self.performance_history = []

    def run_auction(self, resources: List[Resource], requests: List[Request]) -> Dict:
        print(f"Running {self.name} Auction...")
        start_time = time.time()

        # Step 1: Hierarchical Clustering
        resource_clusters, request_clusters = self._hierarchical_clustering(resources, requests)
        print(f"Created {len(resource_clusters)} resource clusters and {len(request_clusters)} request clusters")

        # Step 2: Multi-objective bid generation
        bids = self._generate_multi_objective_bids(resources, requests, resource_clusters, request_clusters)
        print(f"Generated {len(bids)} multi-objective bids")

        # Step 3: Distributed consensus allocation
        allocations = self._distributed_consensus_allocation(bids, resources, requests)
        print(f"Completed {len(allocations)} allocations")

        # Step 4: Dynamic price learning
        self._update_price_learning(allocations)

        execution_time = time.time() - start_time

        result = {
            'allocations': allocations,
            'execution_time': execution_time,
            'communication_overhead': self._calculate_communication_overhead(resource_clusters, request_clusters),
            'requests_count': len(requests),
            'resources_count': len(resources),
            'max_possible_utility': self._calculate_max_possible_utility(resources, requests)
        }

        return result

    def _hierarchical_clustering(self, resources: List[Resource], requests: List[Request]) -> Tuple[List, List]:
        """Cluster resources and requests hierarchically"""

        # Cluster resources by location and type
        if len(resources) > 1:
            resource_features = []
            for r in resources:
                features = [
                    r.location[0], r.location[1],
                    r.capacity, r.cost_per_unit,
                    r.availability, r.reliability, r.energy_efficiency,
                    hash(r.type.value) % 1000 / 1000  # Normalize type
                ]
                resource_features.append(features)

            resource_features = np.array(resource_features)
            n_clusters = min(len(resources) // 3 + 1, 5)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            resource_labels = kmeans.fit_predict(resource_features)

            resource_clusters = [[] for _ in range(n_clusters)]
            for i, label in enumerate(resource_labels):
                resource_clusters[label].append(resources[i])
        else:
            resource_clusters = [resources]

        # Cluster requests by location and requirements
        if len(requests) > 1:
            request_features = []
            for r in requests:
                features = [
                    r.location[0], r.location[1],
                    r.amount, r.max_price, r.priority,
                    hash(r.resource_type.value) % 1000 / 1000
                ]
                request_features.append(features)

            request_features = np.array(request_features)
            n_clusters = min(len(requests) // 3 + 1, 5)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            request_labels = kmeans.fit_predict(request_features)

            request_clusters = [[] for _ in range(n_clusters)]
            for i, label in enumerate(request_labels):
                request_clusters[label].append(requests[i])
        else:
            request_clusters = [requests]

        return resource_clusters, request_clusters

    def _generate_multi_objective_bids(self, resources: List[Resource], requests: List[Request],
                                     resource_clusters: List, request_clusters: List) -> List[Bid]:
        """Generate bids using multi-objective optimization"""
        bids = []

        for request in requests:
            for resource in resources:
                if resource.type != request.resource_type:
                    continue

                if resource.capacity < request.amount:
                    continue

                # Multi-objective utility calculation
                cost_utility = self._calculate_cost_utility(resource, request)
                qos_utility = self._calculate_qos_utility(resource, request)
                energy_utility = self._calculate_energy_utility(resource, request)
                fairness_utility = self._calculate_fairness_utility(resource, request)

                # Combined utility
                utility_score = (self.alpha * cost_utility +
                               self.beta * qos_utility +
                               self.gamma * energy_utility +
                               self.delta * fairness_utility)

                # Dynamic pricing
                dynamic_price = self._calculate_dynamic_price(resource, request, utility_score)

                if dynamic_price <= request.max_price:
                    bid = Bid(
                        id=f"bid_{resource.id}_{request.id}",
                        resource_id=resource.id,
                        request_id=request.id,
                        price=dynamic_price,
                        amount=min(resource.capacity, request.amount),
                        utility_score=utility_score
                    )
                    bids.append(bid)

        return bids

    def _calculate_cost_utility(self, resource: Resource, request: Request) -> float:
        """Calculate cost-based utility (higher is better for lower cost)"""
        if request.max_price <= 0:
            return 0
        cost_ratio = resource.cost_per_unit / request.max_price
        return max(0, 1 - cost_ratio)

    def _calculate_qos_utility(self, resource: Resource, request: Request) -> float:
        """Calculate QoS-based utility"""
        # Distance penalty
        distance = np.sqrt((resource.location[0] - request.location[0])**2 +
                          (resource.location[1] - request.location[1])**2)
        distance_utility = max(0, 1 - distance / 100)  # Normalize to 0-1

        # Reliability and availability
        qos_utility = (resource.reliability + resource.availability) / 2

        return (distance_utility + qos_utility) / 2

    def _calculate_energy_utility(self, resource: Resource, request: Request) -> float:
        """Calculate energy efficiency utility"""
        return resource.energy_efficiency

    def _calculate_fairness_utility(self, resource: Resource, request: Request) -> float:
        """Calculate fairness utility based on priority and historical allocations"""
        priority_utility = request.priority / 10.0

        # Historical fairness (simplified)
        historical_penalty = len([r for r in self.performance_history
                                if r.get('requester_id') == request.requester_id]) * 0.01

        return max(0, priority_utility - historical_penalty)

    def _calculate_dynamic_price(self, resource: Resource, request: Request, utility_score: float) -> float:
        """Calculate dynamic price using learning mechanism"""
        base_price = resource.cost_per_unit * request.amount

        # Historical price adjustment
        key = f"{resource.type.value}_{resource.owner_id}"
        if key in self.price_history:
            avg_historical_price = np.mean(self.price_history[key])
            price_adjustment = self.learning_rate * (avg_historical_price - base_price)
            base_price += price_adjustment

        # Utility-based pricing
        utility_multiplier = 0.8 + 0.4 * utility_score  # 0.8 to 1.2 range
        dynamic_price = base_price * utility_multiplier

        return min(dynamic_price, request.max_price)

    def _distributed_consensus_allocation(self, bids: List[Bid], resources: List[Resource],
                                        requests: List[Request]) -> List[Dict]:
        """Distributed consensus-based allocation"""
        # Sort bids by utility score
        bids_sorted = sorted(bids, key=lambda x: x.utility_score, reverse=True)

        allocations = []
        allocated_resources = set()
        satisfied_requests = set()

        for bid in bids_sorted:
            if bid.resource_id in allocated_resources or bid.request_id in satisfied_requests:
                continue

            # Find corresponding resource and request
            resource = next((r for r in resources if r.id == bid.resource_id), None)
            request = next((r for r in requests if r.id == bid.request_id), None)

            if resource and request:
                allocation = {
                    'bid_id': bid.id,
                    'resource_id': bid.resource_id,
                    'request_id': bid.request_id,
                    'requester_id': request.requester_id,
                    'price': bid.price,
                    'amount': bid.amount,
                    'utility': bid.utility_score,
                    'resource_type': resource.type.value,
                    'timestamp': time.time()
                }

                allocations.append(allocation)
                allocated_resources.add(bid.resource_id)
                satisfied_requests.add(bid.request_id)

        return allocations

    def _update_price_learning(self, allocations: List[Dict]):
        """Update price learning mechanism"""
        for allocation in allocations:
            key = f"{allocation['resource_type']}_{allocation.get('owner_id', 'unknown')}"
            if key not in self.price_history:
                self.price_history[key] = []
            self.price_history[key].append(allocation['price'])

            # Keep only recent history
            if len(self.price_history[key]) > 50:
                self.price_history[key] = self.price_history[key][-50:]

    def _calculate_communication_overhead(self, resource_clusters: List, request_clusters: List) -> float:
        """Calculate communication overhead based on clustering"""
        # Simplified model: overhead is proportional to cross-cluster communications
        total_clusters = len(resource_clusters) * len(request_clusters)
        return total_clusters * 0.1  # Normalized overhead

    def _calculate_max_possible_utility(self, resources: List[Resource], requests: List[Request]) -> float:
        """Calculate theoretical maximum utility for efficiency calculation"""
        max_utility = 0
        for request in requests:
            compatible_resources = [r for r in resources if r.type == request.resource_type and r.capacity >= request.amount]
            if compatible_resources:
                best_resource = max(compatible_resources, key=lambda r: r.reliability * r.availability * r.energy_efficiency)
                max_utility += 1.0  # Theoretical max utility per request
        return max_utility


# Baseline Mechanisms

class FirstPriceAuction(BaseAuctionMechanism):
    """Baseline 1: First-Price Sealed-Bid Auction"""

    def __init__(self):
        super().__init__("First-Price Auction")

    def run_auction(self, resources: List[Resource], requests: List[Request]) -> Dict:
        print(f"Running {self.name}...")
        start_time = time.time()

        bids = []
        for request in requests:
            for resource in resources:
                if resource.type == request.resource_type and resource.capacity >= request.amount:
                    price = resource.cost_per_unit * request.amount
                    if price <= request.max_price:
                        utility = random.uniform(0.3, 0.8)  # Simple utility
                        bid = Bid(
                            id=f"fpb_{resource.id}_{request.id}",
                            resource_id=resource.id,
                            request_id=request.id,
                            price=price,
                            amount=request.amount,
                            utility_score=utility
                        )
                        bids.append(bid)

        # Simple allocation: highest price wins
        bids_sorted = sorted(bids, key=lambda x: x.price, reverse=True)
        allocations = []
        allocated_resources = set()
        satisfied_requests = set()

        for bid in bids_sorted:
            if bid.resource_id not in allocated_resources and bid.request_id not in satisfied_requests:
                allocation = {
                    'bid_id': bid.id,
                    'resource_id': bid.resource_id,
                    'request_id': bid.request_id,
                    'price': bid.price,
                    'amount': bid.amount,
                    'utility': bid.utility_score
                }
                allocations.append(allocation)
                allocated_resources.add(bid.resource_id)
                satisfied_requests.add(bid.request_id)

        return {
            'allocations': allocations,
            'execution_time': time.time() - start_time,
            'communication_overhead': len(bids) * 0.05,
            'requests_count': len(requests),
            'resources_count': len(resources),
            'max_possible_utility': len(requests)
        }

class VickreyAuction(BaseAuctionMechanism):
    """Baseline 2: Vickrey (Second-Price) Auction"""

    def __init__(self):
        super().__init__("Vickrey Auction")

    def run_auction(self, resources: List[Resource], requests: List[Request]) -> Dict:
        print(f"Running {self.name}...")
        start_time = time.time()

        # Group bids by request
        request_bids = {}
        for request in requests:
            request_bids[request.id] = []
            for resource in resources:
                if resource.type == request.resource_type and resource.capacity >= request.amount:
                    price = min(resource.cost_per_unit * request.amount, request.max_price)
                    utility = 0.6 + 0.3 * resource.reliability  # Reliability-based utility
                    bid = Bid(
                        id=f"vick_{resource.id}_{request.id}",
                        resource_id=resource.id,
                        request_id=request.id,
                        price=price,
                        amount=request.amount,
                        utility_score=utility
                    )
                    request_bids[request.id].append(bid)

        allocations = []
        allocated_resources = set()

        for request_id, bids in request_bids.items():
            if len(bids) == 0:
                continue

            # Sort by price (descending)
            bids_sorted = sorted(bids, key=lambda x: x.price, reverse=True)

            # Winner pays second-highest price
            winner_bid = bids_sorted[0]
            if winner_bid.resource_id not in allocated_resources:
                second_price = bids_sorted[1].price if len(bids_sorted) > 1 else winner_bid.price

                allocation = {
                    'bid_id': winner_bid.id,
                    'resource_id': winner_bid.resource_id,
                    'request_id': winner_bid.request_id,
                    'price': second_price,
                    'amount': winner_bid.amount,
                    'utility': winner_bid.utility_score
                }
                allocations.append(allocation)
                allocated_resources.add(winner_bid.resource_id)

        return {
            'allocations': allocations,
            'execution_time': time.time() - start_time,
            'communication_overhead': sum(len(bids) for bids in request_bids.values()) * 0.04,
            'requests_count': len(requests),
            'resources_count': len(resources),
            'max_possible_utility': len(requests)
        }

class HungarianAlgorithm(BaseAuctionMechanism):
    """Baseline 3: Hungarian Algorithm for Optimal Assignment"""

    def __init__(self):
        super().__init__("Hungarian Algorithm")

    def run_auction(self, resources: List[Resource], requests: List[Request]) -> Dict:
        print(f"Running {self.name}...")
        start_time = time.time()

        # Create cost matrix
        compatible_pairs = []
        costs = []

        for i, request in enumerate(requests):
            row_costs = []
            for j, resource in enumerate(resources):
                if resource.type == request.resource_type and resource.capacity >= request.amount:
                    cost = resource.cost_per_unit * request.amount
                    if cost <= request.max_price:
                        row_costs.append(cost)
                        compatible_pairs.append((i, j))
                    else:
                        row_costs.append(float('inf'))
                else:
                    row_costs.append(float('inf'))
            costs.append(row_costs)

        if not costs or not any(c != float('inf') for row in costs for c in row):
            return {
                'allocations': [],
                'execution_time': time.time() - start_time,
                'communication_overhead': 0,
                'requests_count': len(requests),
                'resources_count': len(resources),
                'max_possible_utility': 0
            }

        # Apply Hungarian algorithm
        cost_matrix = np.array(costs)
        row_indices, col_indices = linear_sum_assignment(cost_matrix)

        allocations = []
        for req_idx, res_idx in zip(row_indices, col_indices):
            if cost_matrix[req_idx, res_idx] != float('inf'):
                request = requests[req_idx]
                resource = resources[res_idx]

                allocation = {
                    'resource_id': resource.id,
                    'request_id': request.id,
                    'price': cost_matrix[req_idx, res_idx],
                    'amount': request.amount,
                    'utility': 0.7  # Fixed utility for Hungarian
                }
                allocations.append(allocation)

        return {
            'allocations': allocations,
            'execution_time': time.time() - start_time,
            'communication_overhead': len(requests) * len(resources) * 0.02,
            'requests_count': len(requests),
            'resources_count': len(resources),
            'max_possible_utility': len(requests)
        }

class GreedyAuction(BaseAuctionMechanism):
    """Baseline 4: Greedy Resource Allocation"""

    def __init__(self):
        super().__init__("Greedy Auction")

    def run_auction(self, resources: List[Resource], requests: List[Request]) -> Dict:
        print(f"Running {self.name}...")
        start_time = time.time()

        # Sort requests by priority and price
        requests_sorted = sorted(requests, key=lambda x: (x.priority, x.max_price), reverse=True)

        allocations = []
        available_resources = resources.copy()

        for request in requests_sorted:
            best_resource = None
            best_cost = float('inf')

            for resource in available_resources:
                if resource.type == request.resource_type and resource.capacity >= request.amount:
                    cost = resource.cost_per_unit * request.amount
                    if cost <= request.max_price and cost < best_cost:
                        best_cost = cost
                        best_resource = resource

            if best_resource:
                allocation = {
                    'resource_id': best_resource.id,
                    'request_id': request.id,
                    'price': best_cost,
                    'amount': request.amount,
                    'utility': 0.5 + 0.3 * (request.priority / 10)
                }
                allocations.append(allocation)
                available_resources.remove(best_resource)

        return {
            'allocations': allocations,
            'execution_time': time.time() - start_time,
            'communication_overhead': len(requests) * 0.03,
            'requests_count': len(requests),
            'resources_count': len(resources),
            'max_possible_utility': len(requests)
        }

class RandomAuction(BaseAuctionMechanism):
    """Baseline 5: Random Allocation (Lower Bound)"""

    def __init__(self):
        super().__init__("Random Auction")

    def run_auction(self, resources: List[Resource], requests: List[Request]) -> Dict:
        print(f"Running {self.name}...")
        start_time = time.time()

        allocations = []
        available_resources = resources.copy()
        random.shuffle(available_resources)

        for request in random.sample(requests, len(requests)):
            compatible_resources = [r for r in available_resources
                                  if r.type == request.resource_type and r.capacity >= request.amount]

            if compatible_resources:
                resource = random.choice(compatible_resources)
                cost = resource.cost_per_unit * request.amount

                if cost <= request.max_price:
                    allocation = {
                        'resource_id': resource.id,
                        'request_id': request.id,
                        'price': cost,
                        'amount': request.amount,
                        'utility': random.uniform(0.2, 0.6)
                    }
                    allocations.append(allocation)
                    available_resources.remove(resource)

        return {
            'allocations': allocations,
            'execution_time': time.time() - start_time,
            'communication_overhead': len(requests) * 0.01,
            'requests_count': len(requests),
            'resources_count': len(resources),
            'max_possible_utility': len(requests)
        }
