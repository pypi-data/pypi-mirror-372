"""Session management for Google Colab interactions."""

import logging
import time
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum


class RuntimeType(Enum):
    """Colab runtime types."""
    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"


class SessionStatus(Enum):
    """Session status types."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class ColabSession:
    """Represents a Colab session."""
    notebook_id: str
    session_id: Optional[str] = None
    status: SessionStatus = SessionStatus.DISCONNECTED
    runtime_type: RuntimeType = RuntimeType.CPU
    last_activity: float = 0.0
    connection_time: Optional[float] = None
    error_message: Optional[str] = None
    execution_start_time: Optional[float] = None  # Track execution start
    execution_timeout: float = 300.0  # Default 5 minutes
    is_long_running: bool = False  # Flag for long-running executions
    
    def __post_init__(self):
        """Initialize timestamps."""
        if self.last_activity == 0.0:
            self.last_activity = time.time()
    
    def start_execution(self, is_long_running: bool = False) -> None:
        """Mark the start of code execution."""
        self.execution_start_time = time.time()
        self.is_long_running = is_long_running
        self.status = SessionStatus.BUSY
    
    def end_execution(self) -> None:
        """Mark the end of code execution."""
        self.execution_start_time = None
        self.is_long_running = False
        if self.status == SessionStatus.BUSY:
            self.status = SessionStatus.CONNECTED
    
    def get_execution_duration(self) -> Optional[float]:
        """Get current execution duration if executing."""
        if self.execution_start_time:
            return time.time() - self.execution_start_time
        return None
    
    def is_execution_timeout(self) -> bool:
        """Check if current execution has timed out."""
        duration = self.get_execution_duration()
        return duration is not None and duration > self.execution_timeout


class SessionManager:
    """Manages Colab sessions and their lifecycle."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the session manager."""
        self.config = config
        self.colab_config = config.get("colab", {})
        self.sessions: Dict[str, ColabSession] = {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.max_idle_time = self.colab_config.get("max_idle_time", 3600)  # 1 hour
        self.connection_timeout = self.colab_config.get("connection_timeout", 60)
        self.max_retries = self.colab_config.get("max_retries", 3)
    
    def create_session(self, notebook_id: str, runtime_type: RuntimeType = RuntimeType.CPU) -> ColabSession:
        """Create a new Colab session."""
        session = ColabSession(
            notebook_id=notebook_id,
            runtime_type=runtime_type,
            status=SessionStatus.DISCONNECTED
        )
        
        self.sessions[notebook_id] = session
        self.logger.info(f"Created session for notebook {notebook_id}")
        
        return session
    
    def get_session(self, notebook_id: str) -> Optional[ColabSession]:
        """Get an existing session."""
        return self.sessions.get(notebook_id)
    
    def get_or_create_session(self, notebook_id: str, runtime_type: RuntimeType = RuntimeType.CPU) -> ColabSession:
        """Get existing session or create a new one."""
        session = self.get_session(notebook_id)
        if session is None:
            session = self.create_session(notebook_id, runtime_type)
        return session
    
    def update_session_status(self, notebook_id: str, status: SessionStatus, error_message: Optional[str] = None) -> None:
        """Update session status."""
        session = self.get_session(notebook_id)
        if session:
            session.status = status
            session.last_activity = time.time()
            
            if status == SessionStatus.CONNECTED and session.connection_time is None:
                session.connection_time = time.time()
            elif status == SessionStatus.ERROR:
                session.error_message = error_message
            
            self.logger.info(f"Session {notebook_id} status updated to {status.value}")
    
    def mark_execution_start(self, notebook_id: str, is_long_running: bool = False, custom_timeout: Optional[float] = None) -> None:
        """Mark the start of code execution for a session."""
        session = self.get_or_create_session(notebook_id)
        if custom_timeout:
            session.execution_timeout = custom_timeout
        session.start_execution(is_long_running)
        self.logger.info(f"Execution started for session {notebook_id} (long_running: {is_long_running})")
    
    def mark_execution_end(self, notebook_id: str) -> None:
        """Mark the end of code execution for a session."""
        session = self.get_session(notebook_id)
        if session:
            duration = session.get_execution_duration()
            session.end_execution()
            if duration:
                self.logger.info(f"Execution completed for session {notebook_id} in {duration:.2f} seconds")
    
    def check_execution_timeout(self, notebook_id: str) -> bool:
        """Check if the current execution has timed out."""
        session = self.get_session(notebook_id)
        return session.is_execution_timeout() if session else False
    
    def get_execution_status(self, notebook_id: str) -> Dict[str, Any]:
        """Get detailed execution status for a session."""
        session = self.get_session(notebook_id)
        if not session:
            return {"executing": False, "error": "Session not found"}
        
        is_executing = session.execution_start_time is not None
        duration = session.get_execution_duration()
        is_timeout = session.is_execution_timeout()
        
        return {
            "executing": is_executing,
            "duration": duration,
            "timeout": session.execution_timeout,
            "is_timeout": is_timeout,
            "is_long_running": session.is_long_running,
            "status": session.status.value
        }
    
    def cleanup_timed_out_executions(self) -> List[str]:
        """Clean up sessions with timed-out executions."""
        timed_out_sessions = []
        
        for notebook_id, session in self.sessions.items():
            if session.is_execution_timeout():
                self.logger.warning(f"Execution timeout detected for session {notebook_id}")
                session.end_execution()
                session.status = SessionStatus.CONNECTED  # Reset to connected state
                session.error_message = f"Execution timed out after {session.execution_timeout} seconds"
                timed_out_sessions.append(notebook_id)
        
        return timed_out_sessions
    
    def mark_session_active(self, notebook_id: str) -> None:
        """Mark session as active (update last activity time)."""
        session = self.get_session(notebook_id)
        if session:
            session.last_activity = time.time()
    
    def is_session_idle(self, notebook_id: str) -> bool:
        """Check if session is idle (inactive for too long)."""
        session = self.get_session(notebook_id)
        if not session:
            return True
        
        idle_time = time.time() - session.last_activity
        return idle_time > self.max_idle_time
    
    def is_session_connected(self, notebook_id: str) -> bool:
        """Check if session is connected and active."""
        session = self.get_session(notebook_id)
        if not session:
            return False
        
        return (
            session.status == SessionStatus.CONNECTED and 
            not self.is_session_idle(notebook_id)
        )
    
    def cleanup_idle_sessions(self) -> int:
        """Clean up idle sessions and return count of cleaned sessions."""
        current_time = time.time()
        idle_sessions = []
        
        for notebook_id, session in self.sessions.items():
            idle_time = current_time - session.last_activity
            if idle_time > self.max_idle_time:
                idle_sessions.append(notebook_id)
        
        for notebook_id in idle_sessions:
            self.remove_session(notebook_id)
            self.logger.info(f"Cleaned up idle session: {notebook_id}")
        
        return len(idle_sessions)
    
    def remove_session(self, notebook_id: str) -> bool:
        """Remove a session."""
        if notebook_id in self.sessions:
            del self.sessions[notebook_id]
            self.logger.info(f"Removed session: {notebook_id}")
            return True
        return False
    
    def get_session_info(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session information including execution status."""
        session = self.get_session(notebook_id)
        if not session:
            return None
        
        current_time = time.time()
        idle_time = current_time - session.last_activity
        connection_duration = None
        
        if session.connection_time:
            connection_duration = current_time - session.connection_time
        
        # Get execution information
        execution_info = self.get_execution_status(notebook_id)
        
        return {
            'notebook_id': session.notebook_id,
            'session_id': session.session_id,
            'status': session.status.value,
            'runtime_type': session.runtime_type.value,
            'idle_time': idle_time,
            'connection_duration': connection_duration,
            'is_idle': self.is_session_idle(notebook_id),
            'is_connected': self.is_session_connected(notebook_id),
            'error_message': session.error_message,
            'execution': execution_info
        }
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with their information."""
        sessions_info = []
        for notebook_id in self.sessions:
            info = self.get_session_info(notebook_id)
            if info:
                sessions_info.append(info)
        
        return sessions_info
    
    def get_active_sessions_count(self) -> int:
        """Get count of active (connected) sessions."""
        count = 0
        for notebook_id in self.sessions:
            if self.is_session_connected(notebook_id):
                count += 1
        return count
    
    def set_session_id(self, notebook_id: str, session_id: str) -> None:
        """Set the session ID for a notebook."""
        session = self.get_session(notebook_id)
        if session:
            session.session_id = session_id
            self.logger.info(f"Set session ID for {notebook_id}: {session_id}")
    
    def should_reconnect(self, notebook_id: str) -> bool:
        """Determine if a session should be reconnected."""
        session = self.get_session(notebook_id)
        if not session:
            return False
        
        # Reconnect if disconnected or in error state
        if session.status in [SessionStatus.DISCONNECTED, SessionStatus.ERROR]:
            return True
        
        # Reconnect if idle for too long
        if self.is_session_idle(notebook_id):
            return True
        
        return False
    
    def get_runtime_info(self, notebook_id: str) -> Dict[str, Any]:
        """Get runtime information for a session."""
        session = self.get_session(notebook_id)
        if not session:
            return {}
        
        return {
            'runtime_type': session.runtime_type.value,
            'status': session.status.value,
            'available_types': [rt.value for rt in RuntimeType],
            'recommended_type': RuntimeType.CPU.value  # Default recommendation
        }