from collections.abc import Callable

from .monitor import KnowledgeBaseMonitor


def monitor_pipeline(monitor: KnowledgeBaseMonitor,
                     stage: str,
                     function: Callable,
                     *args,
                     **kwargs):

    monitor.start(stage)

    try:
        result = function(*args, **kwargs)

        duration = monitor.end(stage)

        monitor.record(
            stage=stage,
            status="success",
            duration=duration,
        )

        return result

    except Exception:

        duration = monitor.end(stage)

        monitor.record(
            stage=stage,
            status="failed",
            duration=duration,
        )

        raise 