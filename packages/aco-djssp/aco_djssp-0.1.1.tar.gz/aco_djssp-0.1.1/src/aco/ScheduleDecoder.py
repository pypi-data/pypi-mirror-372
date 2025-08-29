from .misc import is_feasible_sequence
from collections import defaultdict


class ScheduleDecoder:
    def __init__(self, operations):
        self.operations = operations
        self.num_jobs = len(set(op.job_id for op in operations))
        self.num_machines = len(set(op.machine_id for op in operations))

    def decode(self, op_sequence, frozen_indices, current_time, frozen_start_times=None):
        """
        Parameters:
            op_sequence (list of Operation): A full sequence of operations
            frozen_indices (set or list of ints): ops that must remain before current_time
            current_time (int): boundary after which new ops can be scheduled

        Returns:
            dict with keys:
                - "start_times": {op.index: start_time}
                - "end_times": {op.index: end_time}
                - "makespan": max end time across all operations
        """
        # Feasibility check
        if not is_feasible_sequence(op_sequence):
            raise ValueError("Invalid op_sequence: job precedence violated")

        frozen_indices = set(frozen_indices or [])

        # Track when each machine and each job is next available
        machine_available_time = defaultdict(int)
        job_latest_end_time = defaultdict(int)

        start_times = {}
        end_times = {}

        machine_schedule = defaultdict(list)

        #  Block machines used by ongoing frozen operations
        if frozen_indices and frozen_start_times:
            for op in self.operations:
                if op.index in frozen_indices:
                    start = frozen_start_times[op.index]
                    end = start + op.processing_time

                    # If the frozen operation is still running at current_time
                    if start <= current_time < end:
                        machine_id = op.machine_id
                        machine_available_time[machine_id] = end

        # Schedule frozen operations first
        for op in op_sequence:
            if op.index not in frozen_indices:
                continue

            if frozen_start_times is None or op.index not in frozen_start_times:
                raise ValueError(
                    f"Missing original start time for frozen op {op.index}")

            start_time = frozen_start_times[op.index]

            if start_time > current_time:
                raise ValueError(
                    f"Frozen op {op} is scheduled at t={
                        start_time}, which is after current_time={current_time}"
                )

            end_time = start_time + op.processing_time
            start_times[op.index] = start_time
            end_times[op.index] = end_time

            machine_available_time[op.machine_id] = end_time
            job_latest_end_time[op.job_id] = end_time
            machine_schedule[op.machine_id].append((start_time, end_time))

        # Schedule the rest
        for op in op_sequence:
            if op.index in frozen_indices:
                continue

            duration = op.processing_time
            arrival = op.arrival_time
            job_ready = job_latest_end_time.get(op.job_id, 0)
            start_time = max(job_ready, arrival)
            timeline = machine_schedule[op.machine_id]

            while True:
                end_time = start_time + duration
                conflict = False
                for s, e in timeline:
                    if not (end_time <= s or start_time >= e):
                        conflict = True
                        start_time = e  # shift to end of conflicting op
                        break
                if not conflict:
                    break

            end_time = start_time + duration

            start_times[op.index] = start_time
            end_times[op.index] = end_time
            timeline.append((start_time, end_time))
            timeline.sort()

            job_latest_end_time[op.job_id] = end_time
        makespan = max(end_times.values())

        return {
            "start_times": start_times,
            "end_times": end_times,
            "makespan": makespan
        }
