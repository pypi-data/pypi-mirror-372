from ablelabs.neon_v2.notable.core import Base


class SetupData(Base):
    """Setup data management for robot system configuration.
    
    This class manages the robot's system configuration data stored in
    setup_data.toml file, including communication settings, hardware
    configuration, calibration data, and operational parameters.
    """

    async def get_setup_data(self) -> dict:
        """Get all setup data.
        
        Retrieves the complete setup configuration including hardware settings,
        communication parameters, calibration data, and system preferences.
        
        Returns:
            dict: Complete setup data configuration containing:
                - communication: Serial port and network settings
                - env: Environment and operational mode settings
                - hardware: Hardware-specific configuration parameters
                - calibration: Calibration offsets and teaching positions
                - safety: Safety limits and emergency stop settings
                
        Example:
            {
                "communication": {"port": "COM3", "baudrate": 115200},
                "env": {"is_online": true, "debug_mode": false},
                "hardware": {"pipette_count": 2, "axis_count": 6}
            }
        """
        return await self._get("/api/v1/resource/setup-data/")

    async def get_setup_data_keys(self, keys: list[str]) -> dict:
        """Get specific setup data values by keys.
        
        Retrieves only the requested configuration values, which is more
        efficient than loading the entire setup data when only specific
        values are needed.

        Args:
            keys: List of dot-notation keys to retrieve from setup data
                 (e.g., "communication.port", "env.is_online")

        Returns:
            dict: Dictionary containing requested key-value pairs
            
        Example:
            keys = ["communication.port", "env.is_online", "hardware.pipette_count"]
            config = await setup_data.get_setup_data_keys(keys)
            # Returns: {"communication.port": "COM3", "env.is_online": true, ...}
        """
        return await self._post("/api/v1/resource/setup-data/keys", body={"keys": keys})

    async def reload(self) -> dict:
        """Reload setup_data.toml file into memory.
        
        Forces a reload of the setup data configuration from the TOML file.
        This is useful after manually editing the setup_data.toml file or
        during system reconfiguration.
        
        Returns:
            dict: Reload status and any parsing errors
            
        Note:
            Changes to communication settings may require a system restart
            to take full effect. Always verify connectivity after reloading.
        """
        return await self._post("/api/v1/resource/setup-data/reload")

    async def update(self, data: dict) -> dict:
        """Update setup data values.
        
        Modifies specific setup data parameters with new values. Changes
        are applied immediately and persisted to the configuration file.
        
        Args:
            data: Dictionary of configuration keys and new values to update
                 Use dot notation for nested keys (e.g., "communication.port")
        
        Returns:
            dict: Update confirmation and any validation warnings
            
        Example:
            data = {
                "communication.port": "COM4",
                "env.is_online": True,
                "hardware.emergency_stop_enabled": True
            }
            
        Warning:
            Incorrect configuration values can cause system malfunction.
            Always validate settings before applying updates, especially
            for communication and safety-related parameters.
        """
        return await self._post("/api/v1/resource/setup-data/update", body=data)
