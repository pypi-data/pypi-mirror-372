"""
Outcome Logging & Metrics for Syntha Framework.

Provides simple functions to log agent outcomes and query performance metrics.
Supports text file logging, SQLite database, and in-memory tracking.
"""

import json
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class AgentOutcome:
    """Represents a logged agent outcome."""

    timestamp: float
    agent_name: str
    task_type: str
    success: bool
    duration_seconds: Optional[float] = None
    input_context: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentOutcome":
        """Create from dictionary."""
        return cls(**data)


class OutcomeLogger:
    """
    Logs agent outcomes and provides metrics querying capabilities.

    Supports multiple storage backends: memory, text file, and SQLite.
    """

    def __init__(
        self,
        storage_type: str = "memory",
        file_path: Optional[str] = None,
        db_path: Optional[str] = None,
    ):
        """
        Initialize the outcome logger.

        Args:
            storage_type: "memory", "file", or "sqlite"
            file_path: Path for text file logging
            db_path: Path for SQLite database logging
        """
        self.storage_type = storage_type
        self.file_path = file_path
        self.db_path = db_path
        self._memory_outcomes: List[AgentOutcome] = []

        if storage_type == "sqlite" and db_path:
            self._init_sqlite_db()

    def _init_sqlite_db(self):
        """Initialize SQLite database with outcomes table."""
        if self.db_path is None:
            raise ValueError("db_path cannot be None when using SQLite storage")
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                agent_name TEXT NOT NULL,
                task_type TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                duration_seconds REAL,
                input_context TEXT,
                output_data TEXT,
                error_message TEXT,
                metadata TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def log_outcome(
        self,
        agent_name: str,
        task_type: str,
        success: bool,
        duration_seconds: Optional[float] = None,
        input_context: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an agent outcome.

        Args:
            agent_name: Name of the agent
            task_type: Type of task performed
            success: Whether the task was successful
            duration_seconds: How long the task took
            input_context: Context available to the agent
            output_data: Data produced by the agent
            error_message: Error message if task failed
            metadata: Additional metadata
        """
        outcome = AgentOutcome(
            timestamp=time.time(),
            agent_name=agent_name,
            task_type=task_type,
            success=success,
            duration_seconds=duration_seconds,
            input_context=input_context,
            output_data=output_data,
            error_message=error_message,
            metadata=metadata,
        )

        if self.storage_type == "memory":
            self._memory_outcomes.append(outcome)
        elif self.storage_type == "file":
            self._log_to_file(outcome)
        elif self.storage_type == "sqlite":
            self._log_to_sqlite(outcome)

    def _log_to_file(self, outcome: AgentOutcome):
        """Log outcome to text file."""
        if not self.file_path:
            raise ValueError("file_path must be set for file storage")

        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(outcome.to_dict()) + "\n")

    def _log_to_sqlite(self, outcome: AgentOutcome):
        """Log outcome to SQLite database."""
        if not self.db_path:
            raise ValueError("db_path must be set for sqlite storage")

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO outcomes (
                timestamp, agent_name, task_type, success, duration_seconds,
                input_context, output_data, error_message, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                outcome.timestamp,
                outcome.agent_name,
                outcome.task_type,
                outcome.success,
                outcome.duration_seconds,
                json.dumps(outcome.input_context) if outcome.input_context else None,
                json.dumps(outcome.output_data) if outcome.output_data else None,
                outcome.error_message,
                json.dumps(outcome.metadata) if outcome.metadata else None,
            ),
        )
        conn.commit()
        conn.close()

    def get_recent_outcomes(
        self,
        hours: int = 24,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> List[AgentOutcome]:
        """
        Get recent outcomes within the specified time window.

        Args:
            hours: Number of hours to look back
            agent_name: Filter by agent name
            task_type: Filter by task type

        Returns:
            List of matching outcomes
        """
        cutoff_time = time.time() - (hours * 3600)

        if self.storage_type == "memory":
            outcomes = [o for o in self._memory_outcomes if o.timestamp >= cutoff_time]
        elif self.storage_type == "sqlite":
            outcomes = self._query_sqlite_recent(cutoff_time)
        else:  # file
            outcomes = self._read_from_file()
            outcomes = [o for o in outcomes if o.timestamp >= cutoff_time]

        # Apply filters
        if agent_name:
            outcomes = [o for o in outcomes if o.agent_name == agent_name]
        if task_type:
            outcomes = [o for o in outcomes if o.task_type == task_type]

        return sorted(outcomes, key=lambda x: x.timestamp, reverse=True)

    def _read_from_file(self) -> List[AgentOutcome]:
        """Read outcomes from file."""
        if not self.file_path or not Path(self.file_path).exists():
            return []

        outcomes = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    outcomes.append(AgentOutcome.from_dict(data))
                except json.JSONDecodeError:
                    continue
        return outcomes

    def _query_sqlite_recent(self, cutoff_time: float) -> List[AgentOutcome]:
        """Query recent outcomes from SQLite database."""
        if not self.db_path:
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT timestamp, agent_name, task_type, success, duration_seconds,
                   input_context, output_data, error_message, metadata
            FROM outcomes 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """,
            (cutoff_time,),
        )

        outcomes = []
        for row in cursor.fetchall():
            outcomes.append(
                AgentOutcome(
                    timestamp=row[0],
                    agent_name=row[1],
                    task_type=row[2],
                    success=bool(row[3]),
                    duration_seconds=row[4],
                    input_context=json.loads(row[5]) if row[5] else None,
                    output_data=json.loads(row[6]) if row[6] else None,
                    error_message=row[7],
                    metadata=json.loads(row[8]) if row[8] else None,
                )
            )

        conn.close()
        return outcomes

    def get_performance_metrics(
        self, hours: int = 24, agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for the specified time period.

        Args:
            hours: Number of hours to analyze
            agent_name: Specific agent to analyze

        Returns:
            Dictionary with performance metrics
        """
        outcomes = self.get_recent_outcomes(hours, agent_name)

        if not outcomes:
            return {
                "total_tasks": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "error_rate": 0.0,
                "tasks_by_type": {},
                "agents_summary": {},
            }

        total_tasks = len(outcomes)
        successful_tasks = sum(1 for o in outcomes if o.success)
        failed_tasks = total_tasks - successful_tasks

        # Calculate average duration (only for tasks with duration data)
        durations = [
            o.duration_seconds for o in outcomes if o.duration_seconds is not None
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Tasks by type
        tasks_by_type = {}
        for outcome in outcomes:
            task_type = outcome.task_type
            if task_type not in tasks_by_type:
                tasks_by_type[task_type] = {"total": 0, "successful": 0}
            tasks_by_type[task_type]["total"] += 1
            if outcome.success:
                tasks_by_type[task_type]["successful"] += 1

        # Agents summary (if not filtered by agent)
        agents_summary = {}
        if not agent_name:
            for outcome in outcomes:
                agent = outcome.agent_name
                if agent not in agents_summary:
                    agents_summary[agent] = {"total": 0, "successful": 0}
                agents_summary[agent]["total"] += 1
                if outcome.success:
                    agents_summary[agent]["successful"] += 1

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": successful_tasks / total_tasks,
            "error_rate": failed_tasks / total_tasks,
            "average_duration": avg_duration,
            "tasks_by_type": tasks_by_type,
            "agents_summary": agents_summary,
            "time_period_hours": hours,
        }

    def clear_outcomes(self, older_than_hours: Optional[int] = None) -> int:
        """
        Clear outcomes, optionally only those older than specified hours.

        Args:
            older_than_hours: Only clear outcomes older than this many hours

        Returns:
            Number of outcomes cleared
        """
        if older_than_hours is None:
            # Clear all
            if self.storage_type == "memory":
                count = len(self._memory_outcomes)
                self._memory_outcomes.clear()
                return count
            elif self.storage_type == "sqlite":
                if self.db_path is None:
                    raise ValueError("db_path cannot be None when using SQLite storage")
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute("SELECT COUNT(*) FROM outcomes")
                count = cursor.fetchone()[0]
                conn.execute("DELETE FROM outcomes")
                conn.commit()
                conn.close()
                return count
            else:  # file
                if self.file_path and Path(self.file_path).exists():
                    count = len(self._read_from_file())
                    Path(self.file_path).unlink()
                    return count
                return 0
        else:
            # Clear old outcomes
            cutoff_time = time.time() - (older_than_hours * 3600)

            if self.storage_type == "memory":
                old_count = len(self._memory_outcomes)
                self._memory_outcomes = [
                    o for o in self._memory_outcomes if o.timestamp >= cutoff_time
                ]
                return old_count - len(self._memory_outcomes)
            elif self.storage_type == "sqlite":
                if self.db_path is None:
                    raise ValueError("db_path cannot be None when using SQLite storage")
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM outcomes WHERE timestamp < ?", (cutoff_time,)
                )
                count = cursor.fetchone()[0]
                conn.execute("DELETE FROM outcomes WHERE timestamp < ?", (cutoff_time,))
                conn.commit()
                conn.close()
                return count
            else:
                # For file storage, we'd need to rewrite the file
                outcomes = self._read_from_file()
                old_count = len(outcomes)
                recent_outcomes = [o for o in outcomes if o.timestamp >= cutoff_time]

                if self.file_path:
                    with open(self.file_path, "w", encoding="utf-8") as f:
                        for outcome in recent_outcomes:
                            f.write(json.dumps(outcome.to_dict()) + "\n")

                return old_count - len(recent_outcomes)
