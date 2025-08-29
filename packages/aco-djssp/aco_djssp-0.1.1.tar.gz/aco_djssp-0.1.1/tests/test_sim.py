from aco import *
import math
import numpy as np
from pathlib import Path


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
    op.arrival_time = 25
    # Test arrival of an urgent job
    op.priority = 1

    max_index += 1

job_arrival_schedule = {
    25: ops_flat
}

jam = JobArrivalManager(job_arrival_schedule)
map_instance = Map(operations, ants)


sim = Simulator(
    map_instance=map_instance,
    arrival_manager=jam,
    decoder=scheduledecoder,
    max_time=100
)

best_path, schedule, best_makespan = sim.run(
    plot_initial_schedule=True, lambda_disruption=1)

plot_schedule_gantt(best_path, schedule,
                    locked_operations=sim.frozen_at_last_replan)
