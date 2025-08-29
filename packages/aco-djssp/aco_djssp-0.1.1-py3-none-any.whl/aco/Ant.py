import numpy as np
from random import choices


class Ant:
    """
    Ant in MMAS.

    Each ant builds a feasible operation sequence (schedule) by:
      - Respecting job precedence constraints.
      - Respecting frozen (locked) operations.
      - Selecting from eligible operations stochastically according
        to pheromone trails and desirability values.

    Parameters
    alpha : float, default=2
        Controls influence of pheromone trails.
    beta : float, default=2
        Controls influence of heuristic desirability.

    Attributes
    path : list of Operation
        Current sequence of scheduled operations.
    locked_path : list of Operation
        Frozen prefix of operations that must appear at the beginning
        of any constructed path.
    """
    def __init__(self, alpha=2, beta=2):
        # Parameter to control impact of pheromones on path decision making
        self.alpha = alpha

        # Parameter to control impact of desirability on path decision making
        self.beta = beta

        # Path the ant has taken so far
        # Sequence of scheduled operations
        self.path = []

        # Path that the ant must start with
        # This will be all operations that have already happened
        self.locked_path = []

    def set_locked_path(self, locked_operations):
        """
        Set the locked path.

        Parameters
        locked_operations : list of Operations
            Operations that must be scheduled first in order.
        """
        self.locked_path = locked_operations.copy()

    def get_eligible_operations(self, all_operations, locked_indices):
        """
        Returns operations whose job-predecessors have already been scheduled.
        If an operation is the first in a job, it is automatically eligible
        (unless it has already been scheduled)

        Parameters
        all_operations : list of Operations
            Global operation list.
        locked_indices : set of int
            Indices of operations that are frozen in the schedule.

        Returns
        eligible : list of Operations
            Operations whose predecessors are already scheduled or frozen.
            If any operation has priority = 0, only those are returned.
        """
        eligible = []
        scheduled_indices = {
            op.index for op in self.path}.union(locked_indices)

        for op in all_operations:
            # Skip all already scheduled operations
            if op.index in scheduled_indices:
                continue

            # If the operation starts a new job, it is eligible
            if op.operation_id == 0:
                eligible.append(op)
            else:
                # Find the previous operation in the same job
                prev_op = next(
                    (o for o in all_operations
                     if o.job_id == op.job_id and o.operation_id == op.operation_id - 1),
                    None
                )

                if prev_op and prev_op.index in scheduled_indices:
                    eligible.append(op)

        # Priority filter
        if eligible:
            min_priority = min(op.priority for op in eligible)
            # Operations with a priority of 0 need to be scheduled immediately
            if min_priority == 0:
                eligible = [
                    op for op in eligible if op.priority == min_priority]

        return eligible

    def move_probabilities(self, map_instance, eligible_ops):
        """
        Returns the probabilities of an ant going from its current state
        to each other node it has not yet visited
        Parameters
        map_instance : Map
            The global map, containing pheromone and desirability matrices.
        eligible_ops : list of Operation
            Operations currently eligible to be scheduled.

        Returns
        probabilities : ndarray of shape (len(eligible_ops),)
            Normalized probabilities of selecting each operation.
            If denominator is 0 or invalid, a uniform distribution is returned.
        """
        from_op = self.path[-1] if self.path else None

        # Compute probabilities of ant moving to remaining nodes
        numerators = []
        for to_op in eligible_ops:
            i = from_op.index if from_op else None
            j = to_op.index

            # Default values if no previous operation (first move)
            pheromones = map_instance.pheromone_matrix[i][j] if from_op else 1
            desirability = map_instance.desirability_matrix[i][j] if from_op else 1

            numerators.append((pheromones ** self.alpha) *
                              (desirability ** self.beta))

        numerators = np.array(numerators)
        denominator = np.sum(numerators)

        if denominator == 0 or not np.isfinite(denominator):
            # Uniform distribution fallback
            # Necessary to prevent crashing when iterating for too long and some paths fade
            probabilities = np.ones(
                len(eligible_ops)) / len(eligible_ops)
        else:
            probabilities = numerators / denominator

        return probabilities

    def choose_operation(self, map_instance, eligible_ops):
        """
        Choose next operation to schedule given the possible remaining operations

        Parameters
        map_instance : Map
            The global map
        eligible_ops : list of Operation
            Candidate operations.

        Returns
        op : Operation
            The chosen operation.
        """
        # Choose an operation from the choices available
        probabilities = self.move_probabilities(map_instance, eligible_ops)
        return choices(eligible_ops, weights=probabilities)[0]

    def reset(self):
        """
        Reset the ant to its locked position.
        """
        self.path = self.locked_path.copy()

    def construct_schedule(self, map_instance):
        """
        Build a full schedule in valid order.
        Starts with the locked path.
        Repeatedly adds eligible operations until all are scheduled.

        Parameters
        map_instance : Map
            The global map
        """

        self.reset()
        all_ops = map_instance.operations

        # Add locked operations to already scheduled operations
        locked_indices = set(op.index for op in self.locked_path)
        scheduled_indices = set(locked_indices)

        while len(scheduled_indices) < len(all_ops):
            eligible = self.get_eligible_operations(all_ops, scheduled_indices)
            # Double filter
            # This is likely unnecessary
            eligible = [
                op for op in eligible if op.index not in scheduled_indices]

            if not eligible:
                break
            op = self.choose_operation(map_instance, eligible)
            self.path.append(op)
            scheduled_indices.add(op.index)
