# Examples

Real-world usage patterns and configuration examples for StrataRegula v0.2.0.

## Configuration Files

### Prefecture Hierarchy Example

File: `examples/sample_prefectures.yaml`

Demonstrates hierarchical prefecture to region mapping with pattern expansion.

### Traffic Configuration Example  

File: `examples/sample_traffic.yaml`

Shows traffic routing configuration with wildcard patterns.

### Hierarchy Testing

File: `examples/hierarchy_test.py`

Python script for testing hierarchical pattern expansion functionality.

## Simulation Examples

### Bank Queue Simulation

File: `examples/bank_renege_simulation.py`

Banking queue simulation demonstrating discrete event processing.

### Car Wash Simulation

File: `examples/carwash_simulation.py`

Car wash service simulation with resource management.

### Machine Shop Simulation

File: `examples/machine_shop_simulation.py`

Manufacturing process simulation with machine scheduling.

## Usage

To run the examples:

```bash
# Test configuration compilation
strataregula compile examples/sample_prefectures.yaml

# Run hierarchy tests
python examples/hierarchy_test.py

# Run simulations
python examples/bank_renege_simulation.py
python examples/carwash_simulation.py
python examples/machine_shop_simulation.py
```

## Quick Navigation

- [← Back to Documentation Index](../index.md)
- [User Guide](../user-guide/)  
- [Developer Guide](../developer-guide/)
- [API Reference](../api-reference/)
