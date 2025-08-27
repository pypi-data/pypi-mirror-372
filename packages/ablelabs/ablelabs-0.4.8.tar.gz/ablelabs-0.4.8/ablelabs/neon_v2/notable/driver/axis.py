from ablelabs.neon_v2.notable.core import Base
from ablelabs.neon_v2.notable.enums import Axis as AxisEnum


class Axis(Base):
    """Low-level axis control and motion driver interface.
    
    This class provides direct control over individual robot axes including
    X, Y, Z1, Z2, P1, P2. It offers precise motion control, status monitoring,
    and configuration management for each axis independently.
    
    Available Axes:
        - X: X-axis (horizontal movement)
        - Y: Y-axis (horizontal movement) 
        - Z1: Z-axis for pipette mount 1
        - Z2: Z-axis for pipette mount 2
        - P1: Plunger axis for pipette 1
        - P2: Plunger axis for pipette 2
    """
    async def get_max_speed(self) -> dict:
        """Get maximum speed limits for all axes.
        
        Returns:
            dict: Maximum speed values for each axis in mm/s or steps/s
        """
        return await self._get("/api/v1/driver/axis/max-speed")

    async def get_status(self, axis: AxisEnum) -> dict[str, bool]:
        """Get current status of specific axis."""
        return await self._get("/api/v1/driver/axis/status", params={"axis": axis})

    async def get_fault(self, axis: AxisEnum) -> dict[str, bool]:
        """Get fault status for specific axis."""
        return await self._get("/api/v1/driver/axis/fault", params={"axis": axis})

    async def get_error_code(self, axis: AxisEnum) -> str:
        """Get error code for specific axis."""
        return await self._get("/api/v1/driver/axis/error-code", params={"axis": axis})

    async def is_enabled(self, axis: AxisEnum) -> bool:
        """Check if specific axis servo is enabled."""
        return await self._get("/api/v1/driver/axis/is-enabled", params={"axis": axis})

    async def is_home_done(self, axis: AxisEnum) -> bool:
        """Check if homing is completed for specific axis."""
        return await self._get(
            "/api/v1/driver/axis/is-home-done", params={"axis": axis}
        )

    async def is_moving(self, axis: AxisEnum) -> bool:
        """Check if specific axis is currently moving."""
        return await self._get("/api/v1/driver/axis/is-moving", params={"axis": axis})

    async def is_move_done(self, axis: AxisEnum) -> bool:
        """Check if last movement command is completed for specific axis."""
        return await self._get(
            "/api/v1/driver/axis/is-move-done", params={"axis": axis}
        )

    async def get_position(self, axis: AxisEnum, unit: bool = True) -> float:
        """Get current position of specific axis.
        
        Args:
            axis: Target axis (X, Y, Z1, Z2, P1, P2)
            unit: If True, return position in mm; if False, return in steps
            
        Returns:
            dict: Current axis position information
        """
        return await self._get(
            "/api/v1/driver/axis/position", params={"axis": axis, "unit": unit}
        )

    async def set_position(self, axis: AxisEnum, position: float, unit: bool = True) -> None:
        """Force set current position value without actual movement."""
        params = {"axis": axis, "position": position, "unit": unit}
        return await self._post("/api/v1/driver/axis/position", params=params)

    async def get_home_offset(self, axis: AxisEnum) -> float:
        """Get home offset value for specific axis."""
        return await self._get("/api/v1/driver/axis/home-offset", params={"axis": axis})

    async def set_home_offset(self, axis: AxisEnum, home_offset: float) -> None:
        """Set home offset value for specific axis."""
        params = {"axis": axis, "home_offset": home_offset}
        return await self._post("/api/v1/driver/axis/home-offset", params=params)

    async def get_resolution(self, axis: AxisEnum) -> int:
        """Get resolution value for specific axis."""
        return await self._get("/api/v1/driver/axis/resolution", params={"axis": axis})

    async def set_resolution(self, axis: AxisEnum, resolution: float) -> None:
        """Set resolution value for specific axis."""
        params = {"axis": axis, "resolution": resolution}
        return await self._post("/api/v1/driver/axis/resolution", params=params)

    async def enable(self, axis: AxisEnum) -> None:
        """Enable axis servo."""
        return await self._post("/api/v1/driver/axis/enable", params={"axis": axis})

    async def disable(self, axis: AxisEnum) -> None:
        """Disable axis servo."""
        return await self._post("/api/v1/driver/axis/disable", params={"axis": axis})

    async def clear_fault(self, axis: AxisEnum) -> None:
        """Clear fault state for specific axis."""
        return await self._post(
            "/api/v1/driver/axis/clear-fault", params={"axis": axis}
        )

    async def set_digital_output(self, axis: AxisEnum, channel: int, on: bool) -> None:
        """Control digital output connected to specific axis driver."""
        params = {"axis": axis, "channel": channel, "on": on}
        return await self._post("/api/v1/driver/axis/digital-output", params=params)

    async def stop(self, axis: AxisEnum) -> None:
        """Stop axis movement immediately."""
        return await self._post("/api/v1/driver/axis/stop", params={"axis": axis})

    async def home(self, axis: AxisEnum) -> None:
        """Execute homing operation for specified axis.
        
        Performs precise homing by moving the axis until it reaches
        the home sensor, then sets the home position as reference.
        
        Args:
            axis: Target axis (X, Y, Z1, Z2, P1, P2)
            
        Note:
            This function executes asynchronously and returns immediately.
            Use wait_home_done() to wait for completion.
        """
        return await self._post("/api/v1/driver/axis/home", params={"axis": axis})

    async def set_speed(self, axis: AxisEnum, speed: float, unit: bool = True) -> None:
        """Set movement speed for specific axis.
        
        Args:
            axis: Target axis (X, Y, Z1, Z2, P1, P2)
            speed: Movement speed value (must be > 0)
            unit: If True, speed in mm/s; if False, speed in steps/s
            
        Note:
            Speed changes take effect immediately for subsequent movements.
        """
        params = {"axis": axis, "speed": speed, "unit": unit}
        return await self._post("/api/v1/driver/axis/speed", params=params)

    async def set_accel(self, axis: AxisEnum, accel: float, unit: bool = True) -> None:
        """Set acceleration for specific axis."""
        params = {"axis": axis, "accel": accel, "unit": unit}
        return await self._post("/api/v1/driver/axis/accel", params=params)

    async def set_decel(self, axis: AxisEnum, decel: float, unit: bool = True) -> None:
        """Set deceleration for specific axis."""
        params = {"axis": axis, "decel": decel, "unit": unit}
        return await self._post("/api/v1/driver/axis/decel", params=params)

    async def jog(self, axis: AxisEnum, value: float, unit: bool = True) -> None:
        """Move axis continuously at specified speed (0 = stop).
        
        Args:
            axis: Target axis (X, Y, Z1, Z2, P1, P2)
            value: Jog speed (0 = stop)
                - Positive values: move in positive direction
                - Negative values: move in negative direction
                - Zero: stop movement
            unit: Speed unit selection
                - True: speed in mm/s (or unit/s)
                - False: speed in steps/s
                
        Note:
            Jog continues until stopped by calling jog(axis, 0) or another motion command.
            This function executes asynchronously and returns immediately.
        """
        params = {"axis": axis, "value": value, "unit": unit}
        return await self._post("/api/v1/driver/axis/jog", params=params)

    async def step(self, axis: AxisEnum, value: float, unit: bool = True) -> None:
        """Move axis by relative distance from current position.
        
        Args:
            axis: Target axis (X, Y, Z1, Z2, P1, P2)
            value: Relative movement distance (positive or negative)
            unit: If True, distance in mm; if False, distance in steps
            
        Returns:
        Note:
            This function executes asynchronously and returns immediately.
            Use wait_move_done() to wait for completion.
        """
        return await self._post(
            "/api/v1/driver/axis/step",
            params={"axis": axis, "value": value, "unit": unit},
        )

    async def move(self, axis: AxisEnum, position: float, unit: bool = True) -> None:
        """Move axis to absolute position.
        
        Args:
            axis: Target axis (X, Y, Z1, Z2, P1, P2)
            position: Target position value
            unit: If True, position in mm; if False, position in steps
            
        Returns:
        Note:
            This function executes asynchronously and returns immediately.
            Use wait_move_done() to wait for completion.
        """
        return await self._post(
            "/api/v1/driver/axis/move",
            params={"axis": axis, "position": position, "unit": unit},
        )

    async def wait_home_done(self, axis: AxisEnum, timeout: float = None) -> None:
        """Wait for homing operation to complete."""
        params = {"axis": axis}
        if timeout is not None:
            params["timeout"] = timeout
        return await self._post("/api/v1/driver/axis/wait-home-done", params=params)

    async def wait_move_done(self, axis: AxisEnum, timeout: float = None) -> None:
        """Wait for axis movement to complete."""
        params = {"axis": axis}
        if timeout is not None:
            params["timeout"] = timeout
        return await self._post("/api/v1/driver/axis/wait-move-done", params=params)

    async def repeat(
        self,
        axis: AxisEnum,
        pos1: float,
        pos2: float,
        delay_ms: float = 0,
        count: int = 1,
        unit: bool = True,
    ) -> None:
        """Move axis back and forth between two positions."""
        params = {
            "axis": axis,
            "pos1": pos1,
            "pos2": pos2,
            "delay_ms": delay_ms,
            "count": count,
            "unit": unit,
        }
        return await self._post("/api/v1/driver/axis/repeat", params=params)

    async def repeats(self, repeats_request: dict, unit: bool = True) -> None:
        """Request multiple axes to repeat movement simultaneously."""
        return await self._post(
            "/api/v1/driver/axis/repeats", params={"unit": unit}, body=repeats_request
        )
