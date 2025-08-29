import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from .Operation import Operation
from pathlib import Path
import json
from collections import defaultdict
from copy import deepcopy
import matplotlib
import numpy as np
matplotlib.use('Agg')

__all__ = ["generate_operations_from_jobs", "parse_taillard_to_operations",
           "load_instance_with_optimum", "find_critical_path", "apply_local_search", "is_feasible_sequence", "plot_schedule_gantt", "compute_disruption", "plot_pheromone_matrix"]


def generate_operations_from_jobs(jobs):
    """
    Converts job list to flat list of Operation objects

    Parameters:
        jobs: list of jobs
              Each job is a list of (machine_id, processing_time) tuples

    Returns:
        List of Operation objects with unique indices
    """
    operations = []
    op_index = 0
    for job_id, job in enumerate(jobs):
        for operation_id, (machine_id, proc_time) in enumerate(job):
            op = Operation(
                index=op_index,
                job_id=job_id,
                operation_id=operation_id,
                machine_id=machine_id,
                processing_time=proc_time
            )
            operations.append(op)
            op_index += 1
    return operations


def parse_taillard_to_operations(path):
    """
    Parses a Taillard-format JSSP instance file and returns a flat list of Operation objects

    Parameters:
        path (str or Path): Path to the Taillard-format instance file

    Returns:
        List[Operation]: Flat list of Operation objects
    """
    path = Path(path)
    with open(path, "r") as f:
        lines = f.readlines()

    # Remove comments and blank lines
    content_lines = [line.strip() for line in lines if line.strip()
                     and not line.startswith("#")]

    jobs = []

    # Each subsequent line defines a job except the first line
    for line in content_lines[1:]:
        # Split and convert into integers
        line_split_ints = [int(a) for a in line.split()]

        # Get machine ids and processing times
        machines = line_split_ints[::2]
        proc_times = line_split_ints[1::2]

        # Zip them together to get a list of (id, proc_times) pairs
        machine_proc_time_pair = list(zip(machines, proc_times))

        # Add to jobs list
        jobs.append(machine_proc_time_pair)

    # Convert into lsit of Operations and return
    return generate_operations_from_jobs(jobs)


def load_instance_with_optimum(jsplib_path, instance_name):
    metadata_path = Path(jsplib_path) / "instances.json"

    with open(metadata_path, "r") as f:
        instance_metadata = json.load(f)

    matched_entry = next(
        (item for item in instance_metadata if item["name"] == instance_name), None)

    if not matched_entry:
        raise ValueError(f"No metadata found for instance '{
                         instance_name}' in {metadata_path}")

    optimum = matched_entry["optimum"]

    instance_path = Path(jsplib_path) / matched_entry["path"]

    return optimum, parse_taillard_to_operations(instance_path)


def find_critical_path(op_sequence, decoder, frozen_indices, current_time):
    """
    Find the critical path (longest path) through a scheduled list of operations
    """
    schedule = decoder.decode(op_sequence)
    start_times = schedule["start_times"]
    end_times = schedule["end_times"]

    adjacency = _build_adjacency_list(op_sequence, start_times)
    reverse_adj = _build_reverse_adjacency(adjacency)

    # Find operation that finishes last
    end_op = max(end_times.items(), key=lambda x: x[1])[0]

    # Recursively find longest path ending at end_op
    memo = {}
    backtrack = {}
    _dfs_critical_path(end_op, reverse_adj, start_times,
                       end_times, memo, backtrack, visited=set())

    return _reconstruct_path(end_op, backtrack)


def _build_adjacency_list(op_sequence, start_times):
    """
    Create a dictionary where each operation points to the operations that must come after it.
    This includes job order (op1 before op2 in a job) and machine order (op1 scheduled before op2 on same machine)
    """
    adjacency = {op.index: [] for op in op_sequence}

    # Job precedence: Add edges between consecutive operations in the same job
    jobs = defaultdict(list)
    for op in op_sequence:
        jobs[op.job_id].append(op)

    for job_id, ops in jobs.items():
        ops.sort(key=lambda op: op.operation_id)
        for i in range(len(ops) - 1):
            before = ops[i]
            after = ops[i + 1]
            adjacency[before.index].append(after.index)

    # Machine precedence: Add edges based on scheduled order on machines
    machines = defaultdict(list)
    for op in op_sequence:
        machines[op.machine_id].append(op)

    for machine_id, ops in machines.items():
        # Respect the actual schedule
        ops.sort(key=lambda op: start_times[op.index])
        for i in range(len(ops) - 1):
            before = ops[i]
            after = ops[i + 1]
            adjacency[before.index].append(after.index)

    return adjacency


def _build_reverse_adjacency(adjacency):
    """
    Create the reverse of the adjacency graph.
    If A -> B in the original, then B -> A in the reverse.
    This helps backtrack from the end of the schedule.
    """
    reverse_adjacency = defaultdict(list)

    for from_node, to_nodes in adjacency.items():
        for to_node in to_nodes:
            reverse_adjacency[to_node].append(from_node)

    return reverse_adjacency


def _dfs_critical_path(current_op, reverse_adj, start_times, end_times, memo, backtrack, visited=None):
    """
    Recursively find the longest path ending at 'current_op', and remember the best predecessor.
    Includes cycle detection using a set.

    Args:
        current_op: Operation index currently looking at
        reverse_adj: Who comes before this op
        start_times / end_times: From the decoder
        memo: Cache of longest paths already found
        backtrack: Stores the best previous node for each op in the path
    Returns:
        Length of the longest path ending at current_op
    """
    if visited is None:
        visited = set()

    if current_op in visited:
        raise ValueError(f"Cycle detected at operation {
                         current_op}. Check if op_sequence violates precedence constraints.")

    if current_op in memo:
        return memo[current_op]

    visited.add(current_op)

    max_length = 0
    best_pred = None

    for prev_op in reverse_adj[current_op]:
        path_length = _dfs_critical_path(
            prev_op, reverse_adj, start_times, end_times, memo, backtrack, visited)
        path_length += end_times[prev_op] - start_times[prev_op]

        if path_length > max_length:
            max_length = path_length
            best_pred = prev_op

    visited.remove(current_op)
    memo[current_op] = max_length
    if best_pred is not None:
        backtrack[current_op] = best_pred

    return max_length


def _reconstruct_path(end_op, backtrack):
    """
    Reconstruct the critical path by following the backtrack map from end_op back to start
    """
    path = [end_op]
    while path[-1] in backtrack:
        path.append(backtrack[path[-1]])
    path.reverse()
    return path


def apply_local_search(op_sequence, decoder, frozen_indices=None, current_time=0):
    """
    Apply swap-based local search on critical blocks in the given op_sequence.
    Returns the improved op_sequence (or original if no improvement found).
    """
    if frozen_indices is None:
        frozen_indices = set()

    best_sequence = deepcopy(op_sequence)
    best_schedule = decoder.decode(best_sequence, frozen_indices, current_time)
    best_makespan = best_schedule["makespan"]

    # Find critical path
    critical_path = find_critical_path(
        best_sequence, decoder, frozen_indices, current_time)

    # Group critical ops by machine
    index_to_op = {op.index: op for op in best_sequence}
    machine_blocks = defaultdict(list)

    for idx in critical_path:
        op = index_to_op[idx]
        machine_blocks[op.machine_id].append(op)

    #  For each block, try swapping adjacent operations
    for machine_id, ops in machine_blocks.items():
        # Sort operations by start time on that machine
        ops.sort(key=lambda op: best_schedule["start_times"][op.index])

        for i in range(len(ops) - 1):
            op1, op2 = ops[i], ops[i + 1]

            # Do not swap if either operation is frozen
            if op1.index in frozen_indices or op2.index in frozen_indices:
                continue

            # Attempt to swap them in the op_sequencec
            swapped_sequence = deepcopy(best_sequence)

            # Use op.index to find them in swapped_sequence
            op_id_to_pos = {op.index: i for i,
                            op in enumerate(swapped_sequence)}

            i1 = op_id_to_pos[op1.index]
            i2 = op_id_to_pos[op2.index]
            swapped_sequence[i1], swapped_sequence[i2] = swapped_sequence[i2], swapped_sequence[i1]

            # Feasibility check
            if not is_feasible_sequence(swapped_sequence):
                continue

            # Decode and check new makespan
            new_schedule = decoder.decode(
                swapped_sequence, frozen_indices, current_time)
            new_makespan = new_schedule["makespan"]

            if new_makespan < best_makespan:
                best_sequence = swapped_sequence
                best_makespan = new_makespan

    return best_sequence, best_makespan


def is_feasible_sequence(op_sequence):
    """
    Checks that operations of each job occur in the correct order
    """
    job_positions = defaultdict(list)

    for pos, op in enumerate(op_sequence):
        job_positions[op.job_id].append((op.operation_id, pos))

    for job_id, ops in job_positions.items():
        ops.sort(key=lambda x: x[0])  # sort by operation_id
        positions = [pos for _, pos in ops]
        if positions != sorted(positions):
            return False  # operation order is violated
    return True


def plot_schedule_gantt(operations, schedule, locked_operations=None, title="Final Schedule (Gantt Chart)", path="/tmp/gantt.png"):
    if locked_operations is None:
        locked_indices = set()
    else:
        if all(isinstance(op, int) for op in locked_operations):
            locked_indices = set(locked_operations)
        else:
            locked_indices = {op.index for op in locked_operations}

    start_times = schedule["start_times"]
    end_times = schedule["end_times"]

    # Group by machine
    machine_to_ops = defaultdict(list)
    for op in operations:
        machine_to_ops[op.machine_id].append(op)

    fig, ax = plt.subplots(figsize=(12, 6))

    yticks = []
    ytick_labels = []

    colors = plt.get_cmap(
        "tab20", len(set(op.job_id for op in operations)))

    for machine_id, ops in sorted(machine_to_ops.items()):
        yticks.append(machine_id)
        ytick_labels.append(f"Machine {machine_id}")

        for op in ops:
            start = start_times[op.index]
            end = end_times[op.index]
            duration = end - start

            # Each job gets a unique color
            color = colors(op.job_id)

            is_frozen = op.index in locked_indices

            ax.barh(
                y=machine_id,
                width=duration,
                left=start,
                height=0.6,
                color=color,
                edgecolor="black",
                hatch='////' if is_frozen else None,
                linewidth=2 if is_frozen else 1,
                alpha=0.5 if is_frozen else 1.0
            )

            ax.text(
                x=start + duration / 2,
                y=machine_id,
                s=f"J{op.job_id}-O{op.operation_id}",
                va='center',
                ha='center',
                color='white',
                fontsize=8,
                fontweight='bold'
            )

    ax.set_xlabel("Time")
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels)
    ax.set_title(title)
    ax.invert_yaxis()  # Machines go top-down
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    # Legend for jobs
    job_ids = sorted(set(op.job_id for op in operations))
    legend_patches = [mpatches.Patch(color=colors(job_id), label=f"Job {
                                     job_id}") for job_id in job_ids]
    if locked_operations:
        frozen_patch = mpatches.Patch(
            facecolor='white', hatch='////', label='Frozen Op', edgecolor='black')
        legend_patches.append(frozen_patch)
    ax.legend(handles=legend_patches, title="Jobs",
              bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    # Save when running on wsl
    # plt.show()
    plt.savefig(path)


def compute_disruption(path, new_start_times, previous_start_times, locked_indices, current_time, normalise=False):
    """
    Parameters:
        path: List[Operation] The current ant path
        new_start_times: Dict[int, int]  Start times from the new schedule
        previous_start_times: Dict[int, int]  Start times from last global schedule
        locked_indices: Set[int]  Operations that are truly frozen
        current_time: int  Current time of the simulation
        normalise: Bool  Whether or not to normalise the disruption by the number of affected operations

    Returns:
        total_disruption (float): Sum of absolute deviations in start times for previously scheduled ops that have not yet started.
    """
    if previous_start_times is None:
        return 0.0
    total_disruption = 0.0
    n_affected_ops = 0

    for op in path:
        if op.index in locked_indices:
            # Fully frozen ops
            continue

        if op.index in previous_start_times:
            prev_start = previous_start_times[op.index]
            if prev_start > current_time:
                n_affected_ops += 1
                new_start = new_start_times.get(op.index)
                if new_start is not None:
                    total_disruption += abs(new_start - prev_start)

    if normalise:
        total_disruption /= n_affected_ops

    return total_disruption


def plot_pheromone_matrix(matrix, path, title=None):
    fig, ax = plt.subplots(figsize=(6, 6))
    im = ax.imshow(matrix, cmap="viridis")

    # Add colorbar
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    n = matrix.shape[0]

    # Set ticks at cell boundaries
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)

    # Draw grid lines
    ax.grid(which="minor", color="w", linestyle="-", linewidth=0.5)

    # Remove minor tick labels
    ax.tick_params(which="minor", bottom=False, left=False)

    if title:
        ax.set_title(title)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()
