from aco import *
import math
import numpy as np
from pathlib import Path


optimal_makespan, operations = load_instance_with_optimum(
    Path("/home/ben/Documents/Imperial_content/Assignments/JSPLIB/"), "ft06")
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
    op.arrival_time = 225
    max_index += 1

job_arrival_schedule = {
    225: ops_flat
}

jam = JobArrivalManager(job_arrival_schedule)
map_instance = Map(operations, ants)

best_path, best_makespan = map_instance.main(
    scheduledecoder, jam, local_search=True)

schedule = scheduledecoder.decode(best_path)
plot_schedule_gantt(best_path, schedule)
