from ablelabs.neon_v2.notable.core import Base


class Pipette(Base):
    """Pipette configuration management for liquid handling setup.
    
    This class manages pipette configuration for the robot's dual-pipette system.
    Each pipette mount (1 and 2) can be configured with different pipette types
    based on the experimental requirements.
    """

    async def get_pipette(self) -> dict:
        """Get current pipette configuration.
        
        Retrieves the currently configured pipette types for both pipette mounts.
        Each mount can have a different pipette type or be empty.
        
        Returns:
            dict: Current pipette configuration mapping mount positions to pipette types.
                Format: {"1": "pipette_type", "2": "another_pipette"}
                Empty mounts are not included in the response.
                
        Example:
            {
                "1": "8ch_200ul",    # 8-channel 200μL pipette on mount 1
                "2": "1ch_1000ul"    # 1-channel 1000μL pipette on mount 2
            }
        """
        return await self._get("/api/v1/config/pipette/")

    async def set_pipette(self, config: dict[str | int, str]) -> dict:
        """Set pipette configuration for liquid handling.
        
        Configures which pipette codes are mounted on each pipette position.
        This configuration determines the liquid handling capabilities and
        volume ranges available for protocols.
        
        Args:
            config: Dictionary mapping pipette mount positions to pipette codes.
                   Positions can be strings ("1", "2") or integers (1, 2).
                   Values must be valid pipette codes from the pipette library.
                   
        Returns:
            dict: Complete pipette configuration with all positions.
                 Format: {"1": "pipette_code", "2": "pipette_code"}
                 Unassigned positions return None.
            
        Example:
            config = {
                1: "8ch_200ul",       # 8-channel 200μL pipette on mount 1 (int key)
                "2": "1ch_200ul"      # 1-channel 200μL pipette on mount 2 (str key)  
            }
            
            # Returns both positions:
            {
                "1": "8ch_200ul",
                "2": "1ch_200ul"
            }
            
        Available Pipette Codes:
            - "8ch_200ul": 8-channel 200μL pipette (multi-channel)
            - "8ch_1000ul": 8-channel 1000μL pipette (multi-channel)
            - "1ch_200ul": 1-channel 200μL pipette (single-channel)
            - "1ch_20ul": 1-channel 20μL pipette (precision)
            
        Note:
            - Position keys can be strings or integers (both accepted)
            - Positions must be 1 or 2 (dual pipette system)
            - Pipette codes must exist in the pipette library
            - Invalid pipette codes will cause API errors
            - Empty mounts should be omitted from input (will return None)
            - Multi-channel pipettes require compatible labware (96-well plates, etc.)
        """
        return await self._post("/api/v1/config/pipette/", body=config)