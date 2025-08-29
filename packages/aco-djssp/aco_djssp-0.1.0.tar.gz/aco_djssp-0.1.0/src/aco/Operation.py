# Class to define an operation in a job
class Operation:
    def __init__(self, index, job_id, operation_id, machine_id, processing_time, arrival_time=0, priority=1):
        """
        Parameters:
            index (int): Unique index for this operation
            job_id (int): Which job this belongs to
            operation_id (int): Position within the job's sequence (0-based)
            machine_id (int): Resource required to execute this operation
            processing_time (int or float): Duration of the operation
            arrival_time (int or float): Time at which the operation is known.
                                        A time later than 0 indicates an operation scheduled
                                        dynamically.
        """
        self.index = index
        self.job_id = job_id
        self.operation_id = operation_id
        self.machine_id = machine_id
        self.processing_time = processing_time
        self.arrival_time = arrival_time
        self.priority = priority

    def __repr__(self):
        return (f"Op(index={self.index}, job={self.job_id}, op={self.operation_id}, "
                f"machine={self.machine_id}, time={self.processing_time}, arrival_time={self.arrival_time})")
