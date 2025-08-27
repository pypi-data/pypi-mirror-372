from ablelabs.neon_v2.notable.core import Base
from ablelabs.neon_v2.notable.enums import LEDColor


class IO(Base):
    """Input/Output control for robot sensors, indicators, and digital interfaces.
    
    This class manages all I/O operations including digital inputs/outputs,
    environmental sensors, LED controls, and door monitoring. It provides
    real-time monitoring and control of the robot's peripheral systems.
    """
    # Input operations
    async def get_inputs(self) -> dict:
        """Get all digital input (DI) port states.
        
        Returns:
            dict: Current state of all digital input ports
                Format: {"port_1": bool, "port_2": bool, ...}
        """
        return await self._get("/api/v1/driver/io/inputs")

    async def get_outputs(self) -> dict:
        """Get all digital output (DO) port states."""
        return await self._get("/api/v1/driver/io/outputs")

    async def set_outputs(self, outputs: dict) -> dict:
        """Set multiple digital output (DO) pin states."""
        return await self._post("/api/v1/driver/io/outputs", body=outputs)

    async def get_pdo(self, pin) -> float:
        """Get PDO pin PWM state (0-100)."""
        return await self._get("/api/v1/driver/io/pdo", params={"pin": pin})

    async def set_pdo(self, pin: int, value: float | bool) -> dict:
        """Set PDO pin state (ON/OFF or PWM 0-100).
        
        Args:
            pin: PDO pin number
            value: Pin state - bool for ON/OFF, or float (0-100) for PWM
            
        Returns:
            dict: PDO setting confirmation
        """
        return await self._post(
            "/api/v1/driver/io/pdo", params={"pin": pin, "value": value}
        )

    async def get_environment(self) -> dict:
        """Get environment sensor data (temperature, humidity, pressure).
        
        Returns:
            dict: Environmental measurements containing:
                - temperature: Temperature in Celsius
                - humidity: Relative humidity percentage
                - pressure: Atmospheric pressure in hPa
        """
        return await self._get("/api/v1/driver/io/environment")

    async def get_door(self) -> bool:
        """Get door open/closed status.
        
        Returns:
            bool: True if door is open, False if closed
            
        Note:
            Door should be closed during robot operation for safety
        """
        return await self._get("/api/v1/driver/io/door")

    # LED controls
    async def set_led_lamp(self, on: bool) -> None:
        """Turn LED lamp on or off."""
        return await self._post("/api/v1/driver/io/led-lamp", params={"on": on})

    async def set_led_bar(
        self,
        color: LEDColor = LEDColor.GREEN,
        bright_percent: int = 20,
        progress_percent: int = 100,
        blink_time_ms: int = 0,
    ) -> None:
        """Set LED bar color, brightness, progress, and blinking.
        
        Args:
            color: LED color from LEDColor enum
            bright_percent: Brightness level (0-100)
            progress_percent: Progress bar fill percentage (0-100)
            blink_time_ms: Blink interval in milliseconds (0 = no blinking)
            
        Example:
            # Set blue LED at 50% brightness, full progress, no blinking
            await io.set_led_bar(color="BLUE", bright_percent=50, progress_percent=100, blink_time_ms=0)
        """
        params = {
            "color": color,
            "bright_percent": bright_percent,
            "progress_percent": progress_percent,
            "blink_time_ms": blink_time_ms,
        }
        return await self._post("/api/v1/driver/io/led-bar", params=params)

    async def set_led_bar_r(self, percent: int) -> None:
        """Set LED bar red brightness (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/r", params={"percent": percent}
        )

    async def set_led_bar_g(self, percent: int) -> None:
        """Set LED bar green brightness (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/g", params={"percent": percent}
        )

    async def set_led_bar_b(self, percent: int) -> None:
        """Set LED bar blue brightness (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/b", params={"percent": percent}
        )

    async def set_led_bar_w(self, percent: int) -> None:
        """Set LED bar white brightness (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/w", params={"percent": percent}
        )

    async def set_led_bar_percent(self, percent: int) -> None:
        """Set LED bar progress display (0-100)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/percent", params={"percent": percent}
        )

    async def set_led_bar_blink(self, msec: int) -> None:
        """Set LED bar blink time in milliseconds (0 = no blink)."""
        return await self._post(
            "/api/v1/driver/io/led-bar/blink", params={"msec": msec}
        )
