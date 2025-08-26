import argparse
import json
import sys
import csv
import contextlib
from pathlib import Path
from typing import Dict, List, Tuple
from importlib.metadata import version as _pkg_version, PackageNotFoundError

from .auction_mechanisms import (
    MOHAFAuction,
    FirstPriceAuction,
    VickreyAuction,
    HungarianAlgorithm,
    GreedyAuction,
    RandomAuction,
)
from .scenarios import generate_synthetic_scenario
from .core import Resource, Request, ResourceType


MECHANISM_MAP = {
    "mohaf": MOHAFAuction,
    "first_price": FirstPriceAuction,
    "vickrey": VickreyAuction,
    "hungarian": HungarianAlgorithm,
    "greedy": GreedyAuction,
    "random": RandomAuction,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mohaf",
        description="MOHAF: Multi-Objective Hierarchical Auction Framework CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Version flag
    def _get_version() -> str:
        try:
            return _pkg_version("mohaf")
        except PackageNotFoundError:
            return "unknown"
    parser.add_argument("--version", action="version", version=f"mohaf {_get_version()}")

    parser.add_argument(
        "--mechanism",
        choices=list(MECHANISM_MAP.keys()),
        default="mohaf",
        help="Auction mechanism to run",
    )

    # Scenario options
    parser.add_argument("--n-resources", type=int, default=50, help="Number of resources")
    parser.add_argument("--n-requests", type=int, default=30, help="Number of requests")
    parser.add_argument(
        "--scenario-type",
        choices=["balanced", "high_demand", "low_resource"],
        default="balanced",
        help="Synthetic scenario type",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to JSON file containing scenario {resources:[], requests:[]}. Overrides synthetic generation.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")

    # MOHAF-specific weights
    parser.add_argument("--alpha", type=float, default=0.3, help="Cost weight (MOHAF)")
    parser.add_argument("--beta", type=float, default=0.3, help="QoS weight (MOHAF)")
    parser.add_argument("--gamma", type=float, default=0.2, help="Energy weight (MOHAF)")
    parser.add_argument("--delta", type=float, default=0.2, help="Fairness weight (MOHAF)")
    parser.add_argument("--learning-rate", type=float, default=0.01, help="Learning rate (MOHAF)")

    # Output options
    parser.add_argument("--json", action="store_true", help="Output results and metrics as JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--quiet", action="store_true", help="Suppress internal mechanism logs")
    parser.add_argument("--allocations-csv", type=str, default=None, help="Path to write allocations as CSV")
    parser.add_argument("--metrics-json", type=str, default=None, help="Path to write metrics as JSON")

    return parser


def _instantiate_mechanism(args: argparse.Namespace):
    mechanism_name = args.mechanism
    cls = MECHANISM_MAP[mechanism_name]
    if mechanism_name == "mohaf":
        return cls(alpha=args.alpha, beta=args.beta, gamma=args.gamma, delta=args.delta, learning_rate=args.learning_rate)
    return cls()


def _print_human_readable(result: Dict, metrics: Dict) -> None:
    print("Auction completed.\n")
    print("Allocations: {}".format(len(result.get("allocations", []))))
    print("Execution Time: {:.4f}s".format(result.get("execution_time", 0.0)))
    print("Communication Overhead: {}".format(result.get("communication_overhead", 0)))
    print("Requests: {} | Resources: {}".format(result.get("requests_count", 0), result.get("resources_count", 0)))
    print("")
    print("Metrics:")
    print("  Allocation Efficiency: {:.4f}".format(metrics.get("allocation_efficiency", 0.0)))
    print("  Revenue: {:.4f}".format(metrics.get("revenue", 0.0)))
    print("  Satisfaction Rate: {:.4f}".format(metrics.get("satisfaction_rate", 0.0)))
    print("  Resource Utilization: {:.4f}".format(metrics.get("resource_utilization", 0.0)))
    print("  Fairness Index: {:.4f}".format(metrics.get("fairness_index", 0.0)))


def _load_scenario_from_json(path: str) -> Tuple[List[Resource], List[Request]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    def parse_resource(d: Dict) -> Resource:
        return Resource(
            id=d["id"],
            type=ResourceType(d["type"]),
            capacity=float(d["capacity"]),
            cost_per_unit=float(d["cost_per_unit"]),
            location=tuple(d["location"]),
            availability=float(d["availability"]),
            reliability=float(d["reliability"]),
            energy_efficiency=float(d["energy_efficiency"]),
            owner_id=d["owner_id"],
        )

    def parse_request(d: Dict) -> Request:
        return Request(
            id=d["id"],
            requester_id=d["requester_id"],
            resource_type=ResourceType(d["resource_type"]),
            amount=float(d["amount"]),
            max_price=float(d["max_price"]),
            deadline=float(d["deadline"]),
            priority=int(d["priority"]),
            location=tuple(d["location"]),
            qos_requirements=d.get("qos_requirements", {}),
        )

    resources = [parse_resource(r) for r in data.get("resources", [])]
    requests = [parse_request(r) for r in data.get("requests", [])]
    return resources, requests


def _write_allocations_csv(allocations: List[Dict], path: str) -> None:
    if not allocations:
        Path(path).write_text("", encoding="utf-8")
        return
    fieldnames = sorted({k for row in allocations for k in row.keys()})
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(allocations)


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Generate or load scenario
    if args.seed is not None:
        try:
            import random as _random
            import numpy as _np
        except Exception:
            _random = None
            _np = None
        if _random is not None:
            _random.seed(args.seed)
        if _np is not None:
            _np.random.seed(args.seed)

    if args.input:
        resources, requests = _load_scenario_from_json(args.input)
    else:
        resources, requests = generate_synthetic_scenario(
            n_resources=args.n_resources,
            n_requests=args.n_requests,
            scenario_type=args.scenario_type,
        )

    # Instantiate auction mechanism
    mechanism = _instantiate_mechanism(args)

    # Run auction and compute metrics
    if args.quiet:
        with contextlib.redirect_stdout(open(Path.cwd() / "nul" if sys.platform.startswith("win") else "/dev/null", "w")):
            result = mechanism.run_auction(resources, requests)
    else:
        result = mechanism.run_auction(resources, requests)
    metrics = mechanism.calculate_metrics(result)

    if args.json:
        payload = {"result": result, "metrics": metrics}
        if args.pretty:
            print(json.dumps(payload, indent=2))
        else:
            print(json.dumps(payload))
    else:
        _print_human_readable(result, metrics)

    # Optional file outputs
    if args.allocations_csv:
        _write_allocations_csv(result.get("allocations", []), args.allocations_csv)
    if args.metrics_json:
        Path(args.metrics_json).write_text(json.dumps(metrics, indent=2 if args.pretty else None), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())


