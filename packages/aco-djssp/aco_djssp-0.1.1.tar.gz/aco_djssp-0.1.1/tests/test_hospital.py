from pathlib import Path
import csv
from collections import defaultdict
import random
import numpy as np
import matplotlib.pyplot as plt


from aco import (
    Ant, Map, Operation, ScheduleDecoder, JobArrivalManager, Simulator,
    plot_schedule_gantt, compute_disruption
)


# Seeds
random.seed(42)
np.random.seed(42)

# Helpers to load hospital CSV


# Function initally made by ChatGPT and then modified
def load_hospital_schedule(csv_path):
    """
    CSV columns:
      patient_id, op_seq (0-based), doctor (label), duration, orig_start (optional), priority (optional)
    Returns:
      operations: list[Operation]
      doctor_to_mid: dict[str,int] mapping doctor label -> machine_id
      original_schedule: dict with 'start_times', 'end_times', 'makespan' if orig_start present, else None
    """
    rows = []
    csv_path = Path(csv_path)
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(r for r in f if not r.strip().startswith("#"))
        for r in reader:
            rows.append(r)

    # Map doctor labels to machine_ids in order of first appearance
    seen_docs = []
    for r in rows:
        d = r["doctor"].strip()
        if d and d not in seen_docs:
            seen_docs.append(d)
    doctor_to_mid = {doc: i for i, doc in enumerate(seen_docs)}

    # Map patient_id to job_id
    seen_patients = []
    for r in rows:
        p = r["patient_id"].strip()
        if p and p not in seen_patients:
            seen_patients.append(p)
    patient_to_jid = {pid: j for j, pid in enumerate(seen_patients)}

    # Build Operation list
    operations = []
    op_index = 0
    have_orig = True
    start_times = {}
    end_times = {}

    # group rows by patient, then sort by op_seq within patient
    by_patient = defaultdict(list)
    for r in rows:
        by_patient[r["patient_id"].strip()].append(r)
    for pid in by_patient:
        by_patient[pid].sort(key=lambda r: int(r["op_seq"]))

    for pid in seen_patients:
        for r in by_patient[pid]:
            job_id = patient_to_jid[pid]
            operation_id = int(r["op_seq"])
            machine_id = doctor_to_mid[r["doctor"].strip()]
            duration = int(r["duration"])
            priority = int(r["priority"]) if r.get(
                "priority") not in (None, "",) else 1

            op = Operation(
                index=op_index,
                job_id=job_id,
                operation_id=operation_id,
                machine_id=machine_id,
                processing_time=duration,
                arrival_time=0,
                priority=priority
            )
            operations.append(op)

            # original schedule (optional)
            orig_start = r.get("orig_start")
            if orig_start not in (None, "",):
                s = int(orig_start)
                e = s + duration
                start_times[op_index] = s
                end_times[op_index] = e
            else:
                have_orig = False

            op_index += 1

    original_schedule = None
    if have_orig and start_times:
        original_schedule = {
            "start_times": start_times,
            "end_times": end_times,
            "makespan": max(end_times.values())
        }
    return operations, doctor_to_mid, original_schedule


# Metrics helper
def summarise(M_new, start_new, start_old=None, frozen=set(), t_event=None, lam=1.0, path=None):
    if start_old is None or t_event is None:
        D = 0.0
    else:
        D = compute_disruption(
            path=path,
            new_start_times=start_new,
            previous_start_times=start_old,
            locked_indices=frozen,
            current_time=t_event,
            normalise=False
        )
    f = M_new + lam * D
    return D, f


# Quiet simulator (no verbose spam during dynamic replans)

class QuietSimulator(Simulator):
    def replan(self, lambda_disruption=1, max_cycles=1000, best_cost_log=None):
        if self.verbose:
            print(f"[t={self.current_time}] Replanning schedule")

        # Lock already-started ops
        for ant in self.map.ants:
            ant.set_locked_path(self.locked_ops)

        if self.schedule:
            frozen_start_times = {
                op.index: self.schedule["start_times"][op.index]
                for op in self.locked_ops
            }
        else:
            frozen_start_times = None

        self.frozen_at_last_replan = set(self.locked_operations)

        previous_start_times = None if (
            self.current_time == 0 or not self.schedule) else self.schedule["start_times"]

        # Change verbose value
        self.map.main(
            self.decoder,
            self.locked_operations,
            self.current_time,
            local_search=False,
            frozen_start_times=frozen_start_times,
            previous_start_times=previous_start_times,
            lambda_disruption=lambda_disruption,
            max_cycles=max_cycles,
            verbose=False,
            best_cost_log=best_cost_log
        )

        # Decode
        self.schedule = self.decoder.decode(
            self.map.global_best_path,
            self.locked_operations,
            self.current_time,
            frozen_start_times=frozen_start_times
        )


def run_static(operations, doctor_to_mid, outdir="figures", max_cycles=1000, lam=1):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ants = [Ant() for _ in range(10)]
    decoder = ScheduleDecoder(operations)

    # Baseline from the original sequence
    orig_seq = operations[:]
    orig_sched = decoder.decode(orig_seq, frozen_indices=set(), current_time=0)

    amap = Map(operations[:], ants)
    best_log = []
    best_path, best_makespan = amap.main(
        decoder=decoder,
        frozen_indices=set(),
        current_time=0,
        local_search=False,
        frozen_start_times=None,
        previous_start_times=None,
        lambda_disruption=lam,
        max_cycles=max_cycles,
        verbose=False,
        best_cost_log=best_log
    )
    mmas_sched = decoder.decode(
        best_path, frozen_indices=set(), current_time=0)

    # Plots
    plot_schedule_gantt(
        operations, orig_sched,
        title="Original hospital schedule (static baseline)",
        path=str(outdir / "gantt_static_original.png")
    )
    plot_schedule_gantt(
        best_path, mmas_sched,
        title="MMAS-optimised schedule (static)",
        path=str(outdir / "gantt_static_mmas.png")
    )
    plot_best_cost(best_log, title="Static optimisation: best cost over cycles",
                   out="figures/cost_static_single_replan.png")

    # Metrics
    M_orig = orig_sched["makespan"]
    M_mmas = mmas_sched["makespan"]
    print("[Static] makespan: original =", M_orig, " | MMAS =", M_mmas)
    return {
        "orig": {"M": M_orig, "sched": orig_sched, "seq": orig_seq},
        "mmas": {"M": M_mmas, "sched": mmas_sched, "seq": best_path}
    }


# Utility: pick a busy doctor at t_event

def pick_busy_doctor(schedule, operations, t_event):
    start = schedule["start_times"]
    end = schedule["end_times"]
    counts = defaultdict(int)
    for op in operations:
        s = start[op.index]
        e = end[op.index]
        if s <= t_event < e:
            counts[op.machine_id] += 1
    if counts:
        return max(counts, key=counts.get)
    return 0


def run_dynamic_emergency(operations, doctor_to_mid, t_event=25, lam_values=(0, 1, 5), outdir="figures"):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ants = [Ant() for _ in range(max(10, len(operations)))]
    decoder = ScheduleDecoder(operations[:])
    amap = Map(operations[:], ants)

    sim = QuietSimulator(
        map_instance=amap,
        arrival_manager=JobArrivalManager(job_arrival_schedule={}),
        decoder=decoder,
        max_time=t_event,
        verbose=False
    )
    sim.replan(lambda_disruption=1)

    # Advance to t_event (no arrivals yet)
    while sim.current_time < t_event:
        sim.tick(lambda_disruption=1)

    # Snapshot "before"
    before_ref = sim.schedule
    plot_schedule_gantt(
        sim.map.global_best_path, before_ref,
        title=f"Before emergency (t={t_event})",
        path=str(outdir / "gantt_emergency_before.png")
    )

    # Inject an emergency on a busy doctor at t_event
    busy_doc = pick_busy_doctor(before_ref, sim.map.operations, t_event)
    new_job_id = max(op.job_id for op in sim.map.operations) + 1
    new_index = max(op.index for op in sim.map.operations) + 1
    emergency = Operation(
        index=new_index,
        job_id=new_job_id,
        operation_id=0,
        machine_id=busy_doc,
        processing_time=20,
        arrival_time=t_event,
        priority=0
    )
    best_log_emg = []
    sim.arrival_manager = JobArrivalManager({t_event: [emergency]})

    # Tick once at t_event to inject + replan
    sim.tick(lambda_disruption=1, best_cost_log=best_log_emg)
    after_sched = sim.schedule

    plot_schedule_gantt(
        sim.map.global_best_path, after_sched,
        title=f"After emergency insertion (t={t_event})",
        path=str(outdir / "gantt_emergency_after.png")
    )
    plot_best_cost(best_log_emg,
                   title=f"Emergency replan best cost over cycles (t={
                       t_event})",
                   out="figures/cost_emergency_single_replan.png")

    # Metrics across lambdas
    start_old = before_ref["start_times"]
    start_new = after_sched["start_times"]
    M_new = after_sched["makespan"]
    frozen = sim.frozen_at_last_replan
    for lam in lam_values:
        D, f = summarise(M_new, start_new, start_old, frozen,
                         t_event, lam, path=sim.map.global_best_path)
        print(
            f"[Emergency @ t={t_event}] lambda={lam}  M={M_new}  D={D}  f={f}")

    M_before = before_ref["makespan"]
    print(
        f"[Emergency @ t={t_event}] makespan before = {M_before}, after = {M_new}")

    return {"before": before_ref, "after": after_sched}


def run_dynamic_overrun(operations, doctor_to_mid, t_event=40, lam_values=(0, 1, 5), outdir="figures"):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ants = [Ant() for _ in range(len(operations))]
    decoder = ScheduleDecoder(operations[:])
    amap = Map(operations[:], ants)
    sim = QuietSimulator(
        map_instance=amap,
        arrival_manager=JobArrivalManager(job_arrival_schedule={}),
        decoder=decoder,
        max_time=t_event,
        verbose=False
    )
    sim.replan(lambda_disruption=1)

    # Choose an operation to overrun
    # earliest start op across all machines
    sched0 = sim.schedule
    starts = sched0["start_times"]
    first_idx = min(starts, key=lambda k: starts[k])
    base_op = next(
        op for op in sim.map.operations if op.index == first_idx)

    # Create residual op to model overrun (extra 50% of base duration here)
    residual_duration = max(1, int(base_op.processing_time * 0.5))
    residual_idx = max(op.index for op in sim.map.operations) + 1
    residual = Operation(
        index=residual_idx,
        job_id=base_op.job_id,
        operation_id=base_op.operation_id + 1,
        machine_id=base_op.machine_id,
        processing_time=residual_duration,
        arrival_time=t_event,
        priority=0
    )

    # Advance to t_event
    while sim.current_time < t_event:
        sim.tick(lambda_disruption=1)

    # Snapshot before
    before_ref = sim.schedule
    plot_schedule_gantt(
        sim.map.global_best_path, before_ref,
        title=f"Before overrun (t={t_event})",
        path=str(outdir / "gantt_overrun_before.png")
    )

    # Inject residual at t_event and replan
    best_log_over = []
    sim.arrival_manager = JobArrivalManager({t_event: [residual]})
    sim.tick(lambda_disruption=1, best_cost_log=best_log_over)
    after_sched = sim.schedule

    plot_schedule_gantt(
        sim.map.global_best_path, after_sched,
        title=f"After overrun (t={t_event})",
        path=str(outdir / "gantt_overrun_after.png")
    )

    plot_best_cost(best_log_over,
                   title=f"Overrun replan best cost over cycles (t={t_event})",
                   out="figures/cost_overrun_single_replan.png")

    # Metrics
    start_old = before_ref["start_times"]
    start_new = after_sched["start_times"]
    M_new = after_sched["makespan"]
    frozen = sim.frozen_at_last_replan
    for lam in lam_values:
        D, f = summarise(M_new, start_new, start_old, frozen,
                         t_event, lam, path=sim.map.global_best_path)
        print(f"[Overrun @ t={t_event}] lambda={lam}  M={M_new}  D={D}  f={f}")

    M_before = before_ref["makespan"]
    print(
        f"[Overrun @ t={t_event}] makespan before = {M_before}, after = {M_new}")

    return {"before": before_ref, "after": after_sched}


def plot_best_cost(best_cost_log, title="Best cost vs cycles", out="figures/cost_single_replan.png"):
    if not best_cost_log:
        return
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    cycles, costs = zip(*best_cost_log)
    plt.figure(figsize=(9, 4))
    plt.plot(cycles, costs, marker="", linewidth=2)
    plt.xlabel("Cycle")
    plt.ylabel(r"Best cost  $f = M + \lambda \cdot D$")
    plt.title(title)
    plt.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(out)


if __name__ == "__main__":
    # Load hospital CSV
    ops, doc2mid, orig_sched = load_hospital_schedule("./hospital_day.csv")
    print(f"Loaded {len(ops)} operations across {
          len(set(o.job_id for o in ops))} patients and {len(doc2mid)} doctors.")

    if orig_sched is not None:
        plot_schedule_gantt(
            ops, orig_sched,
            title="Original hospital schedule (from CSV)",
            path="figures/gantt_static_original_from_csv.png"
        )

    # Static optimisation
    static_results = run_static(
        ops, doc2mid, outdir="figures", max_cycles=800, lam=1
    )

    # Dynamic emergency insertion at t=25
    run_dynamic_emergency(ops[:], doc2mid, t_event=25,
                          lam_values=(0, 1, 5), outdir="figures")

    # Dynamic overrun at t=40
    run_dynamic_overrun(ops[:], doc2mid, t_event=40,
                        lam_values=(0, 1, 5), outdir="figures")
