from abc import ABC, abstractmethod

import time

class BaseMonitor(ABC):

    @abstractmethod
    def start(self, stage: str) -> None:
        """Start monitoring a pipeline stage."""
        pass

    @abstractmethod
    def end(self, stage: str) -> float:
        """Finish monitoring a pipeline stage and return its duration."""
        pass

    @abstractmethod
    def record(self, stage: str, status: str, duration: float) -> None:
        """Record the result of a pipeline stage."""
        pass


class KnowledgeBaseMonitor(BaseMonitor):

    def __init__(self):
        self.start_time: dict[str, float] = {}
        self.records: list[dict] = []

    def start(self, stage: str) -> None:

        self.start_time[stage] = time.perf_counter()

    def end(self, stage: str) -> None:

        if stage not in self.start_time:
            raise ValueError(
                f"Satge '{stage}' was not started."
            )

        duration = time.perf_counter() - self.start_time[stage]

        return duration

    def record(self, stage: str, status: str, duration: float) -> None:

        self.records.append(
            {
                "stage": stage,
                "status": status,
                "duration_seconds": round(duration, 2)
            }
        )