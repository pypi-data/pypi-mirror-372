# Dynamic Job Shop Scheduling with Ant Colony Optimisation

This repository implements a **Min–Max Ant System (MMAS)** solver for the **Dynamic Job Shop Scheduling Problem (DJSSP)**.  
It is designed to model real-world scheduling environments (e.g. hospitals, manufacturing plants) where:

- Jobs arrive dynamically over time.
- Some operations are already underway and cannot be rescheduled.
- Schedules must balance **makespan minimisation** with **disruption minimisation**.

### Prerequisites

- Python 3.13+
- NumPy
- Matplotlib (for plotting)
- pytest (for testing)

## Installation

```bash
uv pip install aco-djssp
```
Alternatively, cloning the repo and then running 

```bash
uv run tests/test_sim.py
```
should also work and create a local `.venv/`, a python virtual environment with the package installed.

## Running an example
There are several ways of running the package. The most common method will be the one found in `tests/test_sim.py`. Note that this assumes that some benchmarked static JSSP are downloaded. The ones used for testing can be found [here](https://github.com/tamy0612/JSPLIB). 
This test will run a simulation with a dynamic job arrival, and then save the resulting schedule in `/tmp/`. If using Windows, this path will need to be changed. 
A more involved and complicated example can be found in `tests/test_hospital.py`. The way this example works is a little unusual due to plotting requirements, and I would recommend following the approach set out in `test_sim.py`, but it is a good showcase of what can be done. Feel free to hack away at the code if the desired functionality is not present!

## Testing

Tests can be found in `tests/` and can be run with

```bash
uv run pytest
```

or can be manually selected by specifying the file name after `uv run pytest`.

## License
This project is licensed under the MIT license. See `LICENSE.MD` for details.