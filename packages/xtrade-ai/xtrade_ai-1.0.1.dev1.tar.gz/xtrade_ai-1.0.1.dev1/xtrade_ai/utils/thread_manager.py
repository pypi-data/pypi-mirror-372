"""
XTrade-AI Thread Manager

Handles thread-safe operations and proper thread management.
"""

import concurrent.futures
import queue
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from .logger import get_logger
except ImportError:
    import logging

    def get_logger(name):
        return logging.getLogger(name)


class ThreadStatus(Enum):
    """Thread status enumeration."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ThreadInfo:
    """Information about a managed thread."""

    thread_id: str
    name: str
    status: ThreadStatus
    start_time: float
    end_time: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    timeout: Optional[float] = None


class ThreadManager:
    """Manages threads with proper error handling and timeout support."""

    def __init__(self, max_workers: int = 4, default_timeout: float = 300):
        self.logger = get_logger(__name__)
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.active_threads: Dict[str, ThreadInfo] = {}
        self.completed_threads: Dict[str, ThreadInfo] = {}
        self._lock = threading.RLock()
        self._shutdown = False

        # Register cleanup on exit
        import atexit

        atexit.register(self.shutdown)

    def submit_task(
        self,
        task_func: Callable,
        task_name: str,
        timeout: Optional[float] = None,
        *args,
        **kwargs,
    ) -> str:
        """
        Submit a task for execution.

        Args:
            task_func: Function to execute
            task_name: Name of the task
            timeout: Timeout in seconds
            *args, **kwargs: Arguments for the task function

        Returns:
            Thread ID
        """
        if self._shutdown:
            raise RuntimeError("ThreadManager is shutdown")

        thread_id = f"{task_name}_{int(time.time() * 1000)}"
        timeout = timeout or self.default_timeout

        with self._lock:
            thread_info = ThreadInfo(
                thread_id=thread_id,
                name=task_name,
                status=ThreadStatus.IDLE,
                start_time=time.time(),
                timeout=timeout,
            )
            self.active_threads[thread_id] = thread_info

        # Submit to executor
        future = self.executor.submit(
            self._execute_task, thread_id, task_func, *args, **kwargs
        )

        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self._monitor_task, args=(thread_id, future, timeout), daemon=True
        )
        monitor_thread.start()

        self.logger.debug(f"Submitted task: {task_name} (ID: {thread_id})")
        return thread_id

    def _execute_task(
        self, thread_id: str, task_func: Callable, *args, **kwargs
    ) -> Any:
        """Execute a task with proper error handling."""
        try:
            with self._lock:
                if thread_id in self.active_threads:
                    self.active_threads[thread_id].status = ThreadStatus.RUNNING

            result = task_func(*args, **kwargs)

            with self._lock:
                if thread_id in self.active_threads:
                    thread_info = self.active_threads[thread_id]
                    thread_info.status = ThreadStatus.COMPLETED
                    thread_info.end_time = time.time()
                    thread_info.result = result

                    # Move to completed
                    self.completed_threads[thread_id] = thread_info
                    del self.active_threads[thread_id]

            self.logger.debug(f"Task completed: {thread_id}")
            return result

        except Exception as e:
            with self._lock:
                if thread_id in self.active_threads:
                    thread_info = self.active_threads[thread_id]
                    thread_info.status = ThreadStatus.FAILED
                    thread_info.end_time = time.time()
                    thread_info.error = str(e)

                    # Move to completed
                    self.completed_threads[thread_id] = thread_info
                    del self.active_threads[thread_id]

            self.logger.error(f"Task failed: {thread_id} - {e}")
            raise

    def _monitor_task(
        self, thread_id: str, future: concurrent.futures.Future, timeout: float
    ):
        """Monitor a task for timeout."""
        try:
            future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            with self._lock:
                if thread_id in self.active_threads:
                    thread_info = self.active_threads[thread_id]
                    thread_info.status = ThreadStatus.CANCELLED
                    thread_info.end_time = time.time()
                    thread_info.error = f"Task timed out after {timeout} seconds"

                    # Move to completed
                    self.completed_threads[thread_id] = thread_info
                    del self.active_threads[thread_id]

            self.logger.warning(f"Task timed out: {thread_id}")
            future.cancel()
        except Exception as e:
            # Error already handled in _execute_task
            pass

    def get_task_status(self, thread_id: str) -> Optional[ThreadInfo]:
        """Get status of a specific task."""
        with self._lock:
            if thread_id in self.active_threads:
                return self.active_threads[thread_id]
            elif thread_id in self.completed_threads:
                return self.completed_threads[thread_id]
            return None

    def get_task_result(
        self, thread_id: str, wait: bool = True, timeout: float = None
    ) -> Any:
        """
        Get result of a completed task.

        Args:
            thread_id: Thread ID
            wait: Whether to wait for completion
            timeout: Timeout for waiting

        Returns:
            Task result
        """
        if wait:
            start_time = time.time()
            while True:
                thread_info = self.get_task_status(thread_id)
                if thread_info is None:
                    raise ValueError(f"Task {thread_id} not found")

                if thread_info.status in [
                    ThreadStatus.COMPLETED,
                    ThreadStatus.FAILED,
                    ThreadStatus.CANCELLED,
                ]:
                    if thread_info.status == ThreadStatus.FAILED:
                        raise RuntimeError(f"Task failed: {thread_info.error}")
                    elif thread_info.status == ThreadStatus.CANCELLED:
                        raise RuntimeError(f"Task cancelled: {thread_info.error}")
                    return thread_info.result

                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError(f"Timeout waiting for task {thread_id}")

                time.sleep(0.1)
        else:
            thread_info = self.get_task_status(thread_id)
            if thread_info is None:
                raise ValueError(f"Task {thread_id} not found")

            if thread_info.status == ThreadStatus.COMPLETED:
                return thread_info.result
            elif thread_info.status == ThreadStatus.FAILED:
                raise RuntimeError(f"Task failed: {thread_info.error}")
            elif thread_info.status == ThreadStatus.CANCELLED:
                raise RuntimeError(f"Task cancelled: {thread_info.error}")
            else:
                raise RuntimeError(f"Task {thread_id} is still running")

    def cancel_task(self, thread_id: str) -> bool:
        """Cancel a running task."""
        with self._lock:
            if thread_id not in self.active_threads:
                return False

            thread_info = self.active_threads[thread_id]
            thread_info.status = ThreadStatus.CANCELLED
            thread_info.end_time = time.time()
            thread_info.error = "Task cancelled by user"

            # Move to completed
            self.completed_threads[thread_id] = thread_info
            del self.active_threads[thread_id]

        self.logger.info(f"Cancelled task: {thread_id}")
        return True

    def wait_for_all(self, timeout: Optional[float] = None) -> List[str]:
        """Wait for all active tasks to complete."""
        start_time = time.time()

        while True:
            with self._lock:
                active_thread_ids = list(self.active_threads.keys())
                completed_thread_ids = list(self.completed_threads.keys())

            if not active_thread_ids:
                break

            if timeout and (time.time() - start_time) > timeout:
                self.logger.warning(
                    f"Timeout waiting for {len(active_thread_ids)} tasks"
                )
                break

            time.sleep(0.1)

        return completed_thread_ids

    def get_active_tasks(self) -> List[ThreadInfo]:
        """Get list of active tasks."""
        with self._lock:
            return list(self.active_threads.values())

    def get_completed_tasks(self) -> List[ThreadInfo]:
        """Get list of completed tasks."""
        with self._lock:
            return list(self.completed_threads.values())

    def cleanup_completed_tasks(self, max_age: float = 3600):
        """Clean up old completed tasks."""
        current_time = time.time()
        with self._lock:
            expired_threads = []
            for thread_id, thread_info in self.completed_threads.items():
                if (
                    thread_info.end_time
                    and (current_time - thread_info.end_time) > max_age
                ):
                    expired_threads.append(thread_id)

            for thread_id in expired_threads:
                del self.completed_threads[thread_id]

        if expired_threads:
            self.logger.debug(f"Cleaned up {len(expired_threads)} old completed tasks")

    def get_stats(self) -> Dict[str, Any]:
        """Get thread manager statistics."""
        with self._lock:
            active_count = len(self.active_threads)
            completed_count = len(self.completed_threads)

            status_counts = {}
            for thread_info in list(self.active_threads.values()) + list(
                self.completed_threads.values()
            ):
                # Handle both enum and string status
                status_value = (
                    thread_info.status.value
                    if hasattr(thread_info.status, "value")
                    else str(thread_info.status)
                )
                status_counts[status_value] = status_counts.get(status_value, 0) + 1

        return {
            "active_tasks": active_count,
            "completed_tasks": completed_count,
            "max_workers": self.max_workers,
            "status_counts": status_counts,
            "shutdown": self._shutdown,
        }

    def shutdown(self, wait: bool = True, timeout: float = 30):
        """Shutdown the thread manager."""
        if self._shutdown:
            return

        self._shutdown = True
        self.logger.info("Shutting down ThreadManager...")

        # Cancel all active tasks
        with self._lock:
            active_thread_ids = list(self.active_threads.keys())

        for thread_id in active_thread_ids:
            self.cancel_task(thread_id)

        # Shutdown executor with compatibility for different Python versions
        try:
            # Try with timeout parameter (Python 3.9+)
            self.executor.shutdown(wait=wait, timeout=timeout)
        except TypeError:
            # Fallback for older Python versions
            self.executor.shutdown(wait=wait)

        self.logger.info("ThreadManager shutdown complete")


# Global thread manager instance
_thread_manager = ThreadManager()


def get_thread_manager() -> ThreadManager:
    """Get the global thread manager instance."""
    return _thread_manager


def submit_task(
    task_func: Callable,
    task_name: str,
    timeout: Optional[float] = None,
    *args,
    **kwargs,
) -> str:
    """Convenience function for submitting tasks."""
    return _thread_manager.submit_task(task_func, task_name, timeout, *args, **kwargs)


def get_task_result(thread_id: str, wait: bool = True, timeout: float = None) -> Any:
    """Convenience function for getting task results."""
    return _thread_manager.get_task_result(thread_id, wait, timeout)


def wait_for_all(timeout: Optional[float] = None) -> List[str]:
    """Convenience function for waiting for all tasks."""
    return _thread_manager.wait_for_all(timeout)
