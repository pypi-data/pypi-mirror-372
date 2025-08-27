from ablelabs.neon_v2.notable.core import Base


class Robot(Base):
    """Robot action control for protocol execution management.
    
    This class provides methods to control robot protocol execution,
    including status monitoring, pause/resume functionality, and emergency stops.
    """

    async def get_status(self) -> dict:
        """Get current robot status.
        
        Returns:
            dict: Robot status information with keys:
                - status: Current robot state (BOOT, CONNECTED, INITIALIZING, READY, RUNNING, EMERGENCY, STOPPED, ERROR)
                - is_paused: Whether robot is paused
                - error_message: Error description (None if no error)
                - is_operational: Whether robot can perform operations
                - is_error: Whether robot is in error state
                - valid_transitions: Available next states
                
        Key States:
            - BOOT: System startup, hardware communication not established
            - CONNECTED: Hardware connected but requires initialization before use
            
        Note: Other states (INITIALIZING, READY, RUNNING, EMERGENCY, STOPPED, ERROR) 
        may not transition correctly in current implementation - use as reference only.
        """
        return await self._get("/api/v1/action/robot/status")

    async def pause(self) -> None:
        """Pause robot operation.
        
        Pauses all robot operations and prevents execution of subsequent commands.
        The robot completes the current operation before pausing.
        
        Raises:
            APIError: If robot is in error state or cannot be paused
        """
        return await self._post("/api/v1/action/robot/status/pause")

    async def resume(self) -> None:
        """Resume robot operation.
        
        Resumes robot operation from the paused state.
        
        Raises:
            APIError: If robot is not in paused state
        """
        return await self._post("/api/v1/action/robot/status/resume")

    async def stop(self) -> None:
        """Stop robot operation.
        
        Immediately stops current operations and enters STOPPED state.
        Robot must be reset before new operations can begin.
        
        Raises:
            APIError: If robot cannot be stopped
        """
        return await self._post("/api/v1/action/robot/status/stop")

    async def reset(self) -> None:
        """Reset robot to ready state.
        
        Clears error conditions and prepares robot for new operations.
        This does not perform physical homing - use initialize() for stable restart.
        
        Raises:
            APIError: If robot cannot be reset
        """
        return await self._post("/api/v1/action/robot/status/reset")