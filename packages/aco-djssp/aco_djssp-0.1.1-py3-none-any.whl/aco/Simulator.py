from .misc import plot_schedule_gantt, plot_pheromone_matrix


class Simulator:
    """
    Simulation driver for dynamic job-shop execution under MMAS scheduling.

    Parameters
    map_instance : Map
        The global Map
    arrival_manager : object
        Manages job arrivals.
    decoder : object
        Decodes ant paths into schedules.
    max_time : int, default=480
        Maximum simulation horizon (time units).
    verbose : bool, default=True
        If True, prints simulation progress and events.

    Attributes
    ----------
    current_time : int
        Current simulation time.
    max_time : int
        Simulation time horizon.
    verbose : bool
        Controls printing.
    decoder : object
        Decoder instance for schedule evaluation.
    arrival_manager : object
        Arrival manager instance for injecting new jobs.
    map : Map
        Global map.
    schedule : dict or None
        Current decoded schedule.
    locked_operations : set of int
        Operation indices that have already started (cannot be rescheduled).
    frozen_at_last_replan : set of int
        Snapshot of locked operations at the last replanning point.
    """
    def __init__(self, map_instance, arrival_manager, decoder, max_time=480, verbose=True):
        self.current_time = 0
        self.max_time = max_time
        self.verbose = verbose

        self.decoder = decoder
        self.arrival_manager = arrival_manager

        self.map = map_instance
        self.schedule = None

        # Track operations by index that have already started
        self.locked_operations = set()

        self.frozen_at_last_replan = set()

    @property
    def locked_ops(self):
        """
        Return actual Operation objects corresponding to locked operation indices.
        """
        return [op for op in self.map.operations if op.index in self.locked_operations]

    def tick(self, lambda_disruption=1, best_cost_log=None):
        """
        Advance the simulation by one time unit.
        Executes jobs scheduled at the current time.
        If new jobs arrive, expands matrices and triggers a replan.

        Parameters
        lambda_disruption : float, default=1
            Weight on disruption in composite cost function.
        best_cost_log : list or None
            If provided, logs best costs over cycles for plotting.
        """
        if self.verbose:
            print(f"\n===== Time {self.current_time} =====")

        # Simulate execution of jobs at this time
        self.execute_until(self.current_time)

        # Inject new jobs at this time
        new_ops = self.arrival_manager.get_jobs_arriving_at(self.current_time)
        if new_ops:
            if self.verbose:
                print(
                    f"[t={self.current_time}] Injecting new operations: {new_ops}")

            self.map.add_operations(new_ops)
            self.map.expand_matrices(self.map.operations)

            # Reset makespan, path and cost
            self.map.cycle_best_makespan = float("inf")
            self.map.cycle_best_path = None
            self.map.cycle_best_cost = float("inf")

            self.map.global_best_makespan = float("inf")
            self.map.global_best_path = None
            self.map.global_best_cost = float("inf")

            self.replan(lambda_disruption=lambda_disruption,
                        best_cost_log=best_cost_log)

        self.current_time += 1

    def replan(self, lambda_disruption=1, best_cost_log=None):
        """
        Recompute the best schedule given current locked operations.

        Parameters
        lambda_disruption : float, default=1
            Weight for disruption in composite cost function.
        best_cost_log : list or None
            If provided, logs best costs across cycles.
        """
        if self.verbose:
            print(f"[t={self.current_time}] Replanning schedule")

        # Set the locked path for each ant
        for ant in self.map.ants:
            ant.set_locked_path(self.locked_ops)

        # Get the start times for the frozen operations
        frozen_start_times = {
            op.index: self.schedule["start_times"][op.index]
            for op in self.locked_ops
        }

        self.frozen_at_last_replan = set(self.locked_operations)

        if self.current_time == 0:
            previous_start_times = None
        else:
            previous_start_times = self.schedule["start_times"]

        self.map.main(self.decoder, self.locked_operations,
                      self.current_time, local_search=False, frozen_start_times=frozen_start_times, previous_start_times=previous_start_times, lambda_disruption=lambda_disruption, best_cost_log=best_cost_log)
        self.schedule = self.decoder.decode(
            self.map.global_best_path, self.locked_operations, self.current_time, frozen_start_times=frozen_start_times)

    def execute_until(self, time):
        """
        Mark operations as started if they are executing at time param.

        Parameters
        time : int
            Simulation time to check for executing operations.
        """
        if not self.schedule:
            return
        start_times = self.schedule["start_times"]
        end_times = self.schedule["end_times"]

        executing = [(op, start_times[op.index], end_times[op.index])
                     for op in self.map.operations
                     if start_times[op.index] <= time < end_times[op.index]]

        for op, _, _ in executing:
            self.locked_operations.add(op.index)

        if self.verbose:
            print(f"[t={time}] Currently executing operations:")
            for op, start, end in executing:
                print(f"  - {op} (from {start} to {end})")

    def run(self, plot_initial_schedule=False, lambda_disruption=1):
        """
        Run the full simulation until max_time.

        Parameters
        plot_initial_schedule : bool, default=False
            If True, plots the initial schedule as a Gantt chart.
        lambda_disruption : float, default=1
            Weight on disruption in the composite cost.

        Returns
        global_best_path : list of Operation
            Best sequence of operations found.
        schedule : dict
            Decoded schedule of best path.
        global_best_makespan : float
            Makespan of the best path.
        """
        # Initial schedule
        self.replan(lambda_disruption=lambda_disruption)

        # OPtionally plot initial schedule
        if plot_initial_schedule:
            plot_schedule_gantt(self.map.global_best_path, self.schedule,
                                title="Initial schedule", path="/tmp/gantt_initial.png")

        while self.current_time < self.max_time:
            self.tick(lambda_disruption=lambda_disruption)
        print("\nSimulation complete.")
        print(f"Best makespan: {self.map.global_best_makespan}")
        return self.map.global_best_path, self.schedule, self.map.global_best_makespan
