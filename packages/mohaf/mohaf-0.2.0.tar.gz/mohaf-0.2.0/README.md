# MOHAF: Multi-Objective Hierarchical Auction Framework

## Overview
This repository provides the implementation and supporting materials for the paper:

"MOHAF: A Multi-Objective Hierarchical Auction Framework for Scalable and Fair Resource Allocation in IoT Ecosystems"

MOHAF is a distributed resource allocation mechanism for heterogeneous IoT environments.  
It combines hierarchical clustering, submodular optimization, and dynamic pricing to achieve:

- Efficient allocation of resources in large-scale IoT ecosystems  
- Joint optimization of cost, energy efficiency, quality of service (QoS), and fairness  
- Theoretical guarantees with a (1 - 1/e) approximation ratio  
- Perfect fairness across participants (Jain’s Index = 1.000 in experiments)  

We provide code, experimental setup, and references to enable reproducibility and extension of this work.

---
## Repository Contents

```
MOHAF-Resource-Allocation
├─ .gitignore
├─ LICENSE
├─ MOHAF.ipynb
├─ README.md
├─ docs
│  ├─ index.md
│  ├─ mohaf_paper.pdf
│  └─ usage.md
├─ examples
│  ├─ analyze_results.ipynb
│  └─ run_experiments.py
├─ mohaf
│  ├─ __init__.py
│  ├─ auction_mechanisms.py
│  ├─ core.py
│  ├─ scenarios.py
│  └─ utils.py
├─ pyproject.toml
├─ requirements.txt
└─ tests
   ├─ __init__.py
   ├─ test_auction_mechanisms.py
   └─ test_core.py
```
---

## Installation

You can install MOHAF directly from PyPI:

```bash
pip install mohaf
```

## Usage

After installation, you can import MOHAF in your Python scripts:

```python
from mohaf.auction_mechanisms import MOHAFAuction
from mohaf.scenarios import generate_synthetic_scenario

# 1. Initialize the auction mechanism
mohaf_auction = MOHAFAuction(alpha=0.3, beta=0.3, gamma=0.2, delta=0.2)

# 2. Generate a synthetic scenario
resources, requests = generate_synthetic_scenario(n_resources=50, n_requests=30)

# 3. Run the auction
results = mohaf_auction.run_auction(resources, requests)
metrics = mohaf_auction.calculate_metrics(results)

print("Auction completed!")
print(f"  Allocation Efficiency: {metrics['allocation_efficiency']:.3f}")
print(f"  Revenue: ${metrics['revenue']:.2f}")
```

For more detailed examples and to reproduce the experiments from the paper, please see the `examples/` directory and the `MOHAF.ipynb` notebook in the repository.  

---

## Command Line Interface (CLI)

You can also run MOHAF from the terminal without writing code once installed from PyPI.

### Basic usage

```bash
# Default MOHAF mechanism with a balanced synthetic scenario
mohaf

# Specify number of resources/requests and scenario type
mohaf --n-resources 100 --n-requests 60 --scenario-type high_demand

# Choose a different baseline mechanism
mohaf --mechanism greedy
```

### Available mechanisms

- `mohaf` (default)
- `first_price`
- `vickrey`
- `hungarian`
- `greedy`
- `random`

### MOHAF weights

You can tune the MOHAF multi-objective weights and learning rate:

```bash
mohaf --alpha 0.3 --beta 0.3 --gamma 0.2 --delta 0.2 --learning-rate 0.01
```

### Reproducibility and loading scenarios from file

- **Seed**: `--seed 42` to make random generation deterministic.
- **Load from JSON**: Provide a file with `resources` and `requests` arrays matching the `mohaf.core.Resource` and `mohaf.core.Request` fields. Example structure:

```json
{
  "resources": [
    {
      "id": "resource_0",
      "type": "compute",
      "capacity": 50,
      "cost_per_unit": 0.8,
      "location": [0, 0],
      "availability": 0.9,
      "reliability": 0.85,
      "energy_efficiency": 0.75,
      "owner_id": "owner_0"
    }
  ],
  "requests": [
    {
      "id": "request_0",
      "requester_id": "device_0",
      "resource_type": "compute",
      "amount": 20,
      "max_price": 30,
      "deadline": 1730000000.0,
      "priority": 5,
      "location": [10, 10],
      "qos_requirements": {"min_reliability": 0.6, "max_latency": 50}
    }
  ]
}
```

Run with:

```bash
mohaf --input scenario.json
```

### JSON output

Return results and metrics as JSON (for scripting/automation):

```bash
mohaf --json --pretty
```

This prints

```json
{
  "result": { "allocations": [...], "execution_time": 0.123, ... },
  "metrics": { "allocation_efficiency": 0.87, "revenue": 123.45, ... }
}
```

### Saving results to files

- **Allocations to CSV**: `--allocations-csv allocations.csv`
- **Metrics to JSON**: `--metrics-json metrics.json`

### Quiet mode

Suppress internal prints from mechanisms:

```bash
mohaf --quiet
```

### Full help

```bash
mohaf --help
```

Output includes all flags:

- `--mechanism {mohaf,first_price,vickrey,hungarian,greedy,random}`
- `--n-resources INT` and `--n-requests INT`
- `--scenario-type {balanced,high_demand,low_resource}`
- `--alpha --beta --gamma --delta --learning-rate` (MOHAF only)
- `--json` and `--pretty`

---

## Dataset
Experiments rely on the publicly available Google Cluster Data: https://github.com/google/cluster-data  

---

## License
This project is licensed under the MIT License.  

---

## Citation
If you use this repository, please cite the associated paper:

```
@misc{Agrawal2025,
  author       = {Agrawal, Kushagra and Goktas, Polat and Bandopadhyay, Anjan, and Ghosh, Debolina and Jena, Junali Jasmine and Gourisaria, Mahendra Kumar},
  title        = {MOHAF: A Multi-Objective Hierarchical Auction Framework for Scalable and Fair Resource Allocation in IoT Ecosystems},
  year         = {2025},
  eprint       = {2508.14830},
  archivePrefix= {arXiv},
  primaryClass = {cs.DC},
  doi          = {10.48550/arXiv.2508.14830},
  url          = {https://arxiv.org/abs/2508.14830}
}
```

---

📌 Repository link: https://github.com/afrilab/MOHAF-Resource-Allocation/tree/main
