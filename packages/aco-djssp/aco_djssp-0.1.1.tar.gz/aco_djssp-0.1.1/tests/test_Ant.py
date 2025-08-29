from aco import Map, Ant, generate_operations_from_jobs
import math
import numpy as np

jobs = [
    [(0, 5), (1, 3)],  # Job 0
    [(1, 4), (0, 2)]  # Job 1
]

# Convert to list of Operation objects
operations = generate_operations_from_jobs(jobs)

ants = [Ant() for _ in range(10)]
map_instance = Map(operations, ants)


def test_get_eligible_operations():
    my_ant = Ant()

    eligible = my_ant.get_eligible_operations(operations, current_time=0)

    # Assert that the only eligible operations
    # at this initial stage are the ones that start a job
    for op in eligible:
        assert op.operation_id == 0

    # Assert that there are only as many eligible
    # operations as there are jobs
    assert len(eligible) == len(jobs)

    # Manually add the first operation to the schedule of the ant
    my_ant.path.append(operations[0])

    eligible_updated = my_ant.get_eligible_operations(
        operations, current_time=0)

    # Assert that the new eligible operations are the one
    # following operation (0, 5) or the one starting a new job
    for op in eligible_updated:
        assert (op.operation_id == 0 or op.processing_time == 3)


def test_move_probabilities():

    my_ant = Ant()
    eligible = my_ant.get_eligible_operations(operations, current_time=0)
    probabilities = my_ant.move_probabilities(map_instance, eligible)

    # Ensure probabilites add to 1
    assert math.isclose(np.sum(probabilities), 1)

    # Manually add the first operation to the schedule of the ant
    my_ant.path.append(operations[0])

    eligible_updated = my_ant.get_eligible_operations(
        operations, current_time=0)
    probabilities_updated = my_ant.move_probabilities(
        map_instance, eligible_updated)

    # Ensure probabilites add to 1
    assert math.isclose(np.sum(probabilities_updated), 1)


def test_choose_operation():
    my_ant = Ant()

    eligible = my_ant.get_eligible_operations(operations, current_time=0)
    chosen_op = my_ant.choose_operation(map_instance, eligible)

    # Ensure chosen operation is not already in the ant's path
    assert chosen_op not in my_ant.path
    # Ensure that chosen_op is in the list of all operations
    # and the list of eligible operations
    assert chosen_op in operations
    assert chosen_op in eligible

    # Manually add the first operation to the schedule of the ant
    my_ant.path.append(operations[0])
    eligible = my_ant.get_eligible_operations(operations, current_time=0)

    # Increase probability the ant goes to operation 1 from operation 0
    map_instance.pheromone_matrix[0, 1] *= 2

    counter = 0

    for i in range(100):
        chosen_op = my_ant.choose_operation(map_instance, eligible)

        # Ensure chosen operation is not already in the ant's path
        assert chosen_op not in my_ant.path
        # Ensure that chosen_op is in the list of all operations
        # and the list of eligible operations
        assert chosen_op in operations
        assert chosen_op in eligible

        if chosen_op.index == 1:
            counter += 1

    # Ensure the ant is weighted towards going to operation 1
    assert counter > 80


def test_construct_schedule():
    my_ant = Ant()

    my_ant.construct_schedule(map_instance, current_time=0)

    # Ensure all operations are added to the schedule
    assert len(my_ant.path) == len(operations)

    # Ensure starting operation starts a job
    assert my_ant.path[0].operation_id == 0
