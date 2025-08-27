from ablelabs.neon_v2.notable.core import Base


class DriverParam(Base):
    """Driver parameter management for low-level robot configuration.
    
    This class manages driver-level parameters that control the fundamental
    behavior of robot axes, motors, and sensors. These parameters include
    motion profiles, sensor thresholds, and hardware-specific settings.
    """

    async def get_driver_param(self) -> dict:
        """Get all driver parameters.
        
        Retrieves the complete set of driver parameters used by the robot's
        motion control system, sensors, and hardware interfaces.
        
        Returns:
            dict: Complete driver parameter configuration containing:
                - axis_settings: Motion parameters for each axis
                - sensor_config: Sensor calibration and threshold values  
                - hardware_limits: Safety limits and constraints
                - timing_parameters: Motion timing and synchronization settings
        """
        return await self._get("/api/v1/resource/driver-param/")

    async def get_driver_param_keys(self, keys: list[str]) -> dict:
        """Get specific driver parameter values by keys.
        
        Retrieves only the requested parameter values, which is more efficient
        than loading the entire parameter set when only specific values are needed.
        
        Args:
            keys: List of parameter keys to retrieve
            
        Returns:
            dict: Requested parameter values keyed by parameter name
            
        Example:
            keys = ["axis.x.max_speed", "axis.z1.acceleration", "sensor.door.threshold"]
            params = await driver_param.get_driver_param_keys(keys)
        """
        return await self._post(
            "/api/v1/resource/driver-param/keys", body={"keys": keys}
        )

    async def reload(self) -> dict:
        """Reload driver parameters from file.
        
        Forces a reload of driver parameters from the configuration file.
        This is useful after manually editing parameter files or during
        system maintenance and calibration procedures.
        
        Returns:
            dict: Reload status and any validation errors
            
        Warning:
            Reloading parameters may affect robot motion behavior.
            Only perform this operation when the robot is idle and safe.
        """
        return await self._post("/api/v1/resource/driver-param/reload")

    async def update(self, data: dict) -> dict:
        """Update driver parameter values.
        
        Modifies specific driver parameters with new values. Changes take
        effect immediately and persist until the next system restart.
        
        Args:
            data: Dictionary of parameter keys and new values to update
            
        Returns:
            dict: Update confirmation and any validation warnings
            
        Example:
            data = {
                "axis.x.max_speed": 150.0,      # mm/s
                "axis.z1.acceleration": 500.0,   # mm/s²
                "pipette.1.flow_rate_max": 400.0 # μL/s
            }
            
        Warning:
            Incorrect parameter values can cause unsafe robot behavior.
            Only modify parameters if you understand their effects.
        """
        return await self._post("/api/v1/resource/driver-param/update", body=data)
