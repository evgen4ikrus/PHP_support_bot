class JobException(Exception):
    ...


class DeadlineIsExpired(JobException):
    ...


class DeadlineWasAlreadySet(JobException):
    ...
