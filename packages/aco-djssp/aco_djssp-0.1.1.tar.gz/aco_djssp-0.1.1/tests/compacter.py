#!/usr/bin/env python3
import pandas as pd
import sys

REQUIRED_COLS = ["patient_id", "op_seq", "doctor",
                 "duration", "orig_start", "priority"]


def compact_schedule(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all").copy()  # drop blank lines
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Types
    df["op_seq"] = df["op_seq"].astype(int)
    df["duration"] = df["duration"].astype(int)
    df["orig_start"] = df["orig_start"].astype(int)

    # Temp fields
    df["__row_id"] = range(len(df))
    df["__new_start"] = -1

    # Track resource & precedence availability
    last_end_by_patient = {}   # patient_id -> end time of last scheduled op
    last_end_by_doctor = {}    # doctor -> end time of last scheduled op

    max_seq = int(df["op_seq"].max())
    doctors = list(df["doctor"].unique())

    # Schedule layer-by-layer by op_seq; within each doctor, keep original order (orig_start)
    for seq in range(max_seq + 1):
        layer = df[df["op_seq"] == seq]
        for doctor in doctors:
            dsub = layer[layer["doctor"] == doctor].sort_values(
                by=["orig_start", "patient_id", "__row_id"]
            )
            for _, row in dsub.iterrows():
                pid = row["patient_id"]
                dur = int(row["duration"])

                earliest_patient = last_end_by_patient.get(
                    pid, 0) if seq > 0 else 0
                earliest_doctor = last_end_by_doctor.get(doctor, 0)
                start = max(earliest_patient, earliest_doctor)
                end = start + dur

                df.loc[df["__row_id"] == row["__row_id"], "__new_start"] = start
                last_end_by_patient[pid] = end
                last_end_by_doctor[doctor] = end

    # Overwrite orig_start with compacted times, drop temps, and keep original columns only
    df["orig_start"] = df["__new_start"].astype(int)
    df = df.drop(columns=["__row_id", "__new_start"])
    return df[REQUIRED_COLS]


def main(in_csv: str, out_csv: str):
    df = pd.read_csv(in_csv)
    out = compact_schedule(df)
    out.to_csv(out_csv, index=False)
    print(f"Wrote: {out_csv}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compact_and_overwrite.py <input.csv> <output.csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
