class WorkerPoolError(Exception):
    """Base exception for all worker pool errors."""


class PoolStartedError(WorkerPoolError):
    """WorkerPoolAlreadyStartedException is raised when calling _begin() on a pool
    that is already running."""
