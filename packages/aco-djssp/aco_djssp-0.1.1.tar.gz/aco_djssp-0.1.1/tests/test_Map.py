from aco import Map, Ant, Operation, ScheduleDecoder, JobArrivalManager, generate_operations_from_jobs, load_instance_with_optimum
import math
import numpy as np
from pathlib import Path


jobs = [
    [(0, 5), (1, 3)],  # Job 0
    [(1, 4), (0, 2)]  # Job 1
]

# Convert to list of Operation objects
operations = generate_operations_from_jobs(jobs)

ants = [Ant() for _ in range(10)]
map_instance = Map(operations, ants)
scheduledecoder = ScheduleDecoder(operations)


def test_pheromone_decay():
    # Test corect shape
    assert map_instance.pheromone_matrix.shape == map_instance.desirability_matrix.shape

    current_pheromone_matrix = map_instance.pheromone_matrix.copy()
    map_instance.pheromone_decay()
    new_pheromone_matrix = map_instance.pheromone_matrix

    # Test evaporations
    assert (current_pheromone_matrix *
            map_instance.pheromone_evaporation_coefficient == new_pheromone_matrix).all()


def test_construct_solutions():
    map_instance.construct_solutions()

    for ant in map_instance.ants:
        # Ensure that the paths are of length len(Nodes)
        assert len(ant.path) == len(operations)
        # Ensure that no duplicates are in the path
        assert len(ant.path) == len(set(ant.path))


def test_find_best_path():
    best_path, best_makespan = map_instance.find_best_path(scheduledecoder)

    assert (0 < best_makespan and best_makespan <= 14)


def test_step():
    ants = [Ant() for i in range(len(operations))]

    map_instance = Map(operations, ants)

    old_pheromones = map_instance.pheromone_matrix.copy()

    map_instance.step(scheduledecoder)
    new_pheromones = map_instance.pheromone_matrix.copy()

    # Ensure paths have been reset
    assert len(map_instance.ants[0].path) == 0
    # Ensure pheromones change after a step
    assert np.sum(old_pheromones - new_pheromones) != 0


def test_small():
    ants = [Ant() for i in range(2)]

    map_instance = Map(operations, ants)

    # Compute the best schedule
    best_path, best_makespan = map_instance.main(
        scheduledecoder, max_cycles=100, verbose=False)

    # For this simple example, the best makespan is known to be 8
    assert best_makespan == 8


def test_taillard():
    optimal_makespan, operations = load_instance_with_optimum(
        Path("/home/bg721/JSPLIB/"), "ft06")

    ants = [Ant() for i in range(len(operations))]
    scheduledecoder = ScheduleDecoder(operations)
    map_instance = Map(operations, ants)
    best_path, best_makespan = map_instance.main(
        scheduledecoder, local_search=True)

    assert math.isclose(optimal_makespan, best_makespan, rel_tol=0.1)


def test_dynamic():
    optimal_makespan, operations = load_instance_with_optimum(
        Path("/home/bg721/JSPLIB/"), "ft06")
    ants = [Ant() for i in range(len(operations))]
    scheduledecoder = ScheduleDecoder(operations)

    jobs = [
        [(0, 5), (1, 3)]
    ]

    ops_flat = generate_operations_from_jobs(jobs)

    existing_job_ids = {op.job_id for op in operations}
    new_job_id = max(existing_job_ids) + 1

    for op in ops_flat:
        op.job_id = new_job_id

    max_index = operations[-1].index

    for op in ops_flat:
        op.index = max_index + 1
        max_index += 1

    job_arrival_schedule = {
        10: ops_flat
    }

    jam = JobArrivalManager(job_arrival_schedule)
    map_instance = Map(operations, ants)

    best_path, best_makespan = map_instance.main(
        scheduledecoder, jam, local_search=True)
