from ablelabs.neon_v2.notable.core import Base
from ablelabs.neon_v2.notable.enums import ZReference


class UpperModule(Base):
    # Main operation methods
    async def initialize(
        self, home_axes: bool = True, move_to_ready: bool = True
    ) -> None:
        """Initialize robot (homing all axes and move to ready position).

        Args:
            home_axes: Whether to perform homing on all axes
            move_to_ready: Whether to move to ready position after initialization
        """
        body = {"home_axes": home_axes, "move_to_ready": move_to_ready}
        return await self._post("/api/v1/controller/upper-module/initialize", body=body)

    async def move_z_up(self) -> None:
        """Move all Z axes to safe height."""
        return await self._post("/api/v1/controller/upper-module/move-z-up")

    async def move_to(
        self,
        pipette_number: int,
        deck_number: int,
        well: str = "A1",
        z_reference: ZReference = ZReference.TOP,
        xyz_offset: list[float, float, float] = None,
        z_speed: bool | float = False,
    ) -> None:
        """Move safely to specified deck well position.

        Args:
            pipette_number: Pipette number (1-2)
            deck_number: Deck position number (1-12)
            well: Well identifier (e.g., "A1", "B2")
            z_reference: Z-axis reference point from ZReference enum
            xyz_offset: XYZ coordinate offset in mm [X, Y, Z]
            z_speed: Z-axis speed in mm/s (float) or automatic (True=max, False=no change)
        """
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "well": well,
            "z_reference": z_reference,
            "z_speed": z_speed,
        }
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post("/api/v1/controller/upper-module/move-to", body=body)

    async def move_xy(self, x: float, y: float, safe_z_height: bool = True) -> None:
        """Move to XY coordinates after raising Z to safe height.

        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            safe_z_height: Whether to move to safe Z height first
        """
        body = {"x": x, "y": y, "safe_z_height": safe_z_height}
        return await self._post("/api/v1/controller/upper-module/move-xy", body=body)

    async def move_z(
        self,
        pipette_number: int,
        deck_number: int,
        z_reference: ZReference = ZReference.TOP,
        z_offset: float = 0,
        z_speed: bool | float = False,
    ) -> None:
        """Move only Z axis to specified height at current XY position.

        Args:
            pipette_number: Pipette number (1-2)
            deck_number: Deck position number (1-12)
            z_reference: Z-axis reference point from ZReference enum
            z_offset: Z-axis offset in mm (-100 to 100)
            z_speed: Z-axis speed in mm/s (float) or automatic (True=max, False=no change)
        """
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "z_reference": z_reference,
            "z_offset": z_offset,
            "z_speed": z_speed,
        }
        return await self._post("/api/v1/controller/upper-module/move-z", body=body)

    async def step_z(
        self, pipette_number: int, z_offset: float, z_speed: bool | float = False
    ) -> None:
        """Move Z axis by relative distance from current position.

        Args:
            pipette_number: Pipette number (1-2)
            z_offset: Relative Z-axis offset in mm (-100 to 100)
            z_speed: Z-axis speed in mm/s (float) or automatic (True=max, False=no change)
        """
        body = {
            "pipette_number": pipette_number,
            "z_offset": z_offset,
            "z_speed": z_speed,
        }
        return await self._post("/api/v1/controller/upper-module/step-z", body=body)

    async def pick_up_tip(
        self,
        pipette_number: int,
        deck_number: int,
        well: str = "A1",
        xyz_offset: list[float, float, float] = None,
    ) -> None:
        """Pick up tips at specified position.

        Args:
            pipette_number: Pipette number (1-2)
            deck_number: Deck position number (1-12)
            well: Well identifier (e.g., "A1", "B2")
            xyz_offset: XYZ coordinate offset in mm [X, Y, Z]
        """
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "well": well,
        }
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post(
            "/api/v1/controller/upper-module/pick-up-tip", body=body
        )

    async def drop_tip(
        self,
        pipette_number: int,
        deck_number: int = None,
        well: str = "A1",
        xyz_offset: list[float, float, float] = None,
    ) -> None:
        """Drop tips at specified position.

        Args:
            pipette_number: Pipette number (1-2)
            deck_number: Deck position number (1-12), None for trash
            well: Well identifier (e.g., "A1", "B2")
            xyz_offset: XYZ coordinate offset in mm [X, Y, Z]
        """
        body = {"pipette_number": pipette_number, "well": well}
        if deck_number is not None:
            body["deck_number"] = deck_number
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post("/api/v1/controller/upper-module/drop-tip", body=body)

    async def ready_plunger(
        self, pipette_number: int, flow_rate: bool | float = False
    ) -> None:
        """Move plunger to ready position for aspiration (first stop).
        
        This moves the plunger to the first stop position, which is the standard
        position for aspiration and dispense operations.
        
        IMPORTANT: This operation must be performed when the tip is NOT submerged
        in liquid to prevent liquid from being drawn into the pipette accidentally.

        Args:
            pipette_number: Pipette number (1-2)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
        """
        body = {"pipette_number": pipette_number, "flow_rate": flow_rate}
        return await self._post(
            "/api/v1/controller/upper-module/ready-plunger", body=body
        )

    async def blow_out(
        self, pipette_number: int, flow_rate: bool | float = False
    ) -> None:
        """Blow out remaining liquid in tip (second stop).
        
        This moves the plunger to the second stop position to expel any
        remaining liquid from the tip after dispensing.

        Args:
            pipette_number: Pipette number (1-2)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
        """
        body = {"pipette_number": pipette_number, "flow_rate": flow_rate}
        return await self._post("/api/v1/controller/upper-module/blow-out", body=body)

    async def drop_plunger(self, pipette_number: int) -> None:
        """Move plunger down for tip ejection.

        Args:
            pipette_number: Pipette number (1-2)
        """
        body = {"pipette_number": pipette_number}
        return await self._post(
            "/api/v1/controller/upper-module/drop-plunger", body=body
        )

    async def aspirate(
        self,
        pipette_number: int,
        volume: float | list[float],
        flow_rate: bool | float,
        z_offset: float = 0,
        pause_sec: float = 0,
    ) -> None:
        """Aspirate specified volume of liquid.

        Args:
            pipette_number: Pipette number (1-2)
            volume: Volume to aspirate in μL (>0, ≤200). Can be single value or list for multi-aspirate
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
            z_offset: Z-axis offset in mm (-100 to 100)
            pause_sec: Pause duration after aspiration in seconds (0-600)
            
        Example:
            # Single aspirate
            await upper_module.aspirate(1, 100.0, 50.0, z_offset=1.0, pause_sec=0.5)
            
            # Multi-aspirate for 8-channel pipette
            await upper_module.aspirate(1, [100.0, 150.0, 200.0], True)
        """
        body = {
            "pipette_number": pipette_number,
            "volume": volume,
            "flow_rate": flow_rate,
            "z_offset": z_offset,
            "pause_sec": pause_sec,
        }
        return await self._post("/api/v1/controller/upper-module/aspirate", body=body)

    async def dispense(
        self,
        pipette_number: int,
        volume: float,
        flow_rate: bool | float,
        z_offset: float = 0,
        pause_sec: float = 0,
    ) -> None:
        """Dispense specified volume of liquid.

        Args:
            pipette_number: Pipette number (1-2)
            volume: Volume to dispense in μL (0-200)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
            z_offset: Z-axis offset in mm (-100 to 100)
            pause_sec: Pause duration after dispensing in seconds (0-600)
        """
        body = {
            "pipette_number": pipette_number,
            "volume": volume,
            "flow_rate": flow_rate,
            "z_offset": z_offset,
            "pause_sec": pause_sec,
        }
        return await self._post("/api/v1/controller/upper-module/dispense", body=body)

    async def mix(
        self,
        pipette_number: int,
        cycle: int,
        volume: float,
        flow_rate: bool | float,
        delay: float = 0,
        z_offset: float = 0,
    ) -> None:
        """Mix liquid at current position.

        Args:
            pipette_number: Pipette number (1-2)
            cycle: Number of mixing cycles (1-100)
            volume: Volume to mix in μL (0-200)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
            delay: Delay between cycles in seconds (0-10)
            z_offset: Z-axis offset in mm (-100 to 100)
        """
        body = {
            "pipette_number": pipette_number,
            "cycle": cycle,
            "volume": volume,
            "flow_rate": flow_rate,
            "delay": delay,
            "z_offset": z_offset,
        }
        return await self._post("/api/v1/controller/upper-module/mix", body=body)

    # Estimation methods
    async def estimate_initialize(
        self, home_axes: bool = True, move_to_ready: bool = True
    ) -> None:
        """Estimate time for initialization.

        Args:
            home_axes: Whether to perform homing on all axes
            move_to_ready: Whether to move to ready position after initialization
        """
        body = {"home_axes": home_axes, "move_to_ready": move_to_ready}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/initialize", body=body
        )

    async def estimate_move_z_up(self) -> None:
        """Estimate time for moving all Z axes up."""
        return await self._post("/api/v1/controller/upper-module/estimate/move-z-up")

    async def estimate_move_to(
        self,
        pipette_number: int,
        deck_number: int,
        well: str = "A1",
        z_reference: ZReference = ZReference.TOP,
        xyz_offset: list[float, float, float] = None,
        z_speed: bool | float = False,
    ) -> None:
        """Estimate time for move_to operation.

        Args:
            pipette_number: Pipette number (1-2)
            deck_number: Deck position number (1-12)
            well: Well identifier (e.g., "A1", "B2")
            z_reference: Z-axis reference point from ZReference enum
            xyz_offset: XYZ coordinate offset in mm [X, Y, Z]
            z_speed: Z-axis speed in mm/s (float) or automatic (True=max, False=no change)
        """
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "well": well,
            "z_reference": z_reference,
            "z_speed": z_speed,
        }
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post(
            "/api/v1/controller/upper-module/estimate/move-to", body=body
        )

    async def estimate_move_xy(
        self, x: float, y: float, safe_z_height: bool = True
    ) -> None:
        """Estimate time for XY movement.

        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            safe_z_height: Whether to move to safe Z height first
        """
        body = {"x": x, "y": y, "safe_z_height": safe_z_height}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/move-xy", body=body
        )

    async def estimate_move_z(
        self,
        pipette_number: int,
        deck_number: int,
        z_reference: ZReference = ZReference.TOP,
        z_offset: float = 0,
        z_speed: bool | float = False,
    ) -> None:
        """Estimate time for Z movement.

        Args:
            pipette_number: Pipette number (1-2)
            deck_number: Deck position number (1-12)
            z_reference: Z-axis reference point from ZReference enum
            z_offset: Z-axis offset in mm (-100 to 100)
            z_speed: Z-axis speed in mm/s (float) or automatic (True=max, False=no change)
        """
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "z_reference": z_reference,
            "z_offset": z_offset,
            "z_speed": z_speed,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/move-z", body=body
        )

    async def estimate_step_z(
        self, pipette_number: int, z_offset: float, z_speed: bool | float = False
    ) -> None:
        """Estimate time for Z step movement.

        Args:
            pipette_number: Pipette number (1-2)
            z_offset: Relative Z-axis offset in mm (-100 to 100)
            z_speed: Z-axis speed in mm/s (float) or automatic (True=max, False=no change)
        """
        body = {
            "pipette_number": pipette_number,
            "z_offset": z_offset,
            "z_speed": z_speed,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/step-z", body=body
        )

    async def estimate_pick_up_tip(
        self,
        pipette_number: int,
        deck_number: int,
        well: str = "A1",
        xyz_offset: list[float, float, float] = None,
    ) -> None:
        """Estimate time for pick_up_tip operation.

        Args:
            pipette_number: Pipette number (1-2)
            deck_number: Deck position number (1-12)
            well: Well identifier (e.g., "A1", "B2")
            xyz_offset: XYZ coordinate offset in mm [X, Y, Z]
        """
        body = {
            "pipette_number": pipette_number,
            "deck_number": deck_number,
            "well": well,
        }
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post(
            "/api/v1/controller/upper-module/estimate/pick-up-tip", body=body
        )

    async def estimate_drop_tip(
        self,
        pipette_number: int,
        deck_number: int = None,
        well: str = "A1",
        xyz_offset: list[float, float, float] = None,
    ) -> None:
        """Estimate time for drop_tip operation.

        Args:
            pipette_number: Pipette number (1-2)
            deck_number: Deck position number (1-12), None for trash
            well: Well identifier (e.g., "A1", "B2")
            xyz_offset: XYZ coordinate offset in mm [X, Y, Z]
        """
        body = {"pipette_number": pipette_number, "well": well}
        if deck_number is not None:
            body["deck_number"] = deck_number
        if xyz_offset is not None:
            body["xyz_offset"] = xyz_offset
        return await self._post(
            "/api/v1/controller/upper-module/estimate/drop-tip", body=body
        )

    async def estimate_ready_plunger(
        self, pipette_number: int, flow_rate: bool | float = False
    ) -> None:
        """Estimate time for plunger ready operation (first stop).
        
        Calculates the estimated time to move plunger to first stop position.
        
        IMPORTANT: This operation must be performed when the tip is NOT submerged
        in liquid to prevent liquid from being drawn into the pipette accidentally.

        Args:
            pipette_number: Pipette number (1-2)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
        """
        body = {"pipette_number": pipette_number, "flow_rate": flow_rate}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/ready-plunger", body=body
        )

    async def estimate_blow_out(
        self, pipette_number: int, flow_rate: bool | float = False
    ) -> None:
        """Estimate time for blow out operation (second stop).
        
        Calculates the estimated time to move plunger to second stop position.

        Args:
            pipette_number: Pipette number (1-2)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
        """
        body = {"pipette_number": pipette_number, "flow_rate": flow_rate}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/blow-out", body=body
        )

    async def estimate_drop_plunger(self, pipette_number: int) -> None:
        """Estimate time for plunger drop operation.

        Args:
            pipette_number: Pipette number (1-2)
        """
        body = {"pipette_number": pipette_number}
        return await self._post(
            "/api/v1/controller/upper-module/estimate/drop-plunger", body=body
        )

    async def estimate_aspirate(
        self,
        pipette_number: int,
        volume: float,
        flow_rate: bool | float,
        z_offset: float = 0,
        pause_sec: float = 0,
    ) -> None:
        """Estimate time for aspirate operation.

        Args:
            pipette_number: Pipette number (1-2)
            volume: Volume to aspirate in μL (0-200)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
            z_offset: Z-axis offset in mm (-100 to 100)
            pause_sec: Pause duration after aspiration in seconds (0-600)
        """
        body = {
            "pipette_number": pipette_number,
            "volume": volume,
            "flow_rate": flow_rate,
            "z_offset": z_offset,
            "pause_sec": pause_sec,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/aspirate", body=body
        )

    async def estimate_dispense(
        self,
        pipette_number: int,
        volume: float,
        flow_rate: bool | float,
        z_offset: float = 0,
        pause_sec: float = 0,
    ) -> None:
        """Estimate time for dispense operation.

        Args:
            pipette_number: Pipette number (1-2)
            volume: Volume to dispense in μL (0-200)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
            z_offset: Z-axis offset in mm (-100 to 100)
            pause_sec: Pause duration after dispensing in seconds (0-600)
        """
        body = {
            "pipette_number": pipette_number,
            "volume": volume,
            "flow_rate": flow_rate,
            "z_offset": z_offset,
            "pause_sec": pause_sec,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/dispense", body=body
        )

    async def estimate_mix(
        self,
        pipette_number: int,
        cycle: int,
        volume: float,
        flow_rate: bool | float,
        delay: float = 0,
        z_offset: float = 0,
    ) -> None:
        """Estimate time for mix operation.

        Args:
            pipette_number: Pipette number (1-2)
            cycle: Number of mixing cycles (1-100)
            volume: Volume to mix in μL (0-200)
            flow_rate: Flow rate in μL/s (0-500) or automatic (True=max, False=no change)
            delay: Delay between cycles in seconds (0-10)
            z_offset: Z-axis offset in mm (-100 to 100)
        """
        body = {
            "pipette_number": pipette_number,
            "cycle": cycle,
            "volume": volume,
            "flow_rate": flow_rate,
            "delay": delay,
            "z_offset": z_offset,
        }
        return await self._post(
            "/api/v1/controller/upper-module/estimate/mix", body=body
        )
