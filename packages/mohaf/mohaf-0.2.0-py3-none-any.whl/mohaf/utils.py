
from typing import Dict

def calculate_allocation_efficiency(result: Dict) -> float:
    if not result.get('allocations'):
        return 0.0
    total_utility = sum(alloc.get('utility', 0) for alloc in result['allocations'])
    max_possible_utility = result.get('max_possible_utility', 1)
    return total_utility / max_possible_utility if max_possible_utility > 0 else 0

def calculate_total_revenue(result: Dict) -> float:
    if not result.get('allocations'):
        return 0.0
    return sum(alloc.get('price', 0) * alloc.get('amount', 0) for alloc in result['allocations'])

def calculate_satisfaction_rate(result: Dict) -> float:
    if not result.get('requests_count'):
        return 0.0
    satisfied = len(result.get('allocations', []))
    return satisfied / result['requests_count']

def calculate_resource_utilization(result: Dict) -> float:
    if not result.get('resources_count'):
        return 0.0
    utilized = len(set(alloc.get('resource_id') for alloc in result.get('allocations', [])))
    return utilized / result['resources_count']

def calculate_fairness_index(result: Dict) -> float:
    """Jain's Fairness Index"""
    if not result.get('allocations'):
        return 1.0
    utilities = [alloc.get('utility', 0) for alloc in result['allocations']]
    if not utilities:
        return 1.0
    sum_utilities = sum(utilities)
    sum_squared = sum(u**2 for u in utilities)
    n = len(utilities)
    if sum_squared == 0:
        return 1.0
    return (sum_utilities**2) / (n * sum_squared)
