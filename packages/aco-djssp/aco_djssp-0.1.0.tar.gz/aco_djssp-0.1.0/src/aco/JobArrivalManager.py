class JobArrivalManager:
    def __init__(self, job_arrival_schedule):
        """
        Parameters:
            job_arrival_schedule (dict[int, list[Operation]]):
                Mapping from time step to list of operations arriving at that time
                e.g. 10 : [Operation1, Operation2 ...]
        """
        self.schedule = job_arrival_schedule

    def get_jobs_arriving_at(self, time):
        """
        Return the list ofnew operations arriving at this time
        """
        return self.schedule.pop(time, [])
