from ablelabs.neon_v2.notable.core import Base


class Deck(Base):
    """Deck configuration management for labware positioning.
    
    This class manages the robot deck layout configuration, allowing users to
    define which labware types are placed at each deck position (1-12).
    """

    async def get_deck(self) -> dict:
        """Get current deck configuration.
        
        Retrieves the current labware configuration for all deck positions.
        Each position (1-12) can contain a specific labware type or be empty.
        
        Returns:
            dict: Current deck configuration mapping deck positions to labware types.
                Format: {"1": "labware_type", "2": "another_labware", ...}
                Empty positions are not included in the response.
                
        Example:
            {
                "1": "ablelabs_tip_box_200",
                "2": "nest_12_reservoir_360102", 
                "3": "spl_96_well_plate_30096",
                "12": "ablelabs_trash"
            }
        """
        return await self._get("/api/v1/config/deck/")

    async def set_deck(self, config: dict[str | int, str]) -> dict:
        """Set deck configuration for labware positioning.
        
        Configures which labware codes are placed at specific deck positions.
        This configuration is used by the robot to calculate correct positioning
        and movement paths for liquid handling operations.
        
        Args:
            config: Dictionary mapping deck positions to labware codes.
                   Positions can be strings ("1"-"12") or integers (1-12).
                   Values must be valid labware codes from the labware library.
                   
        Returns:
            dict: Complete deck configuration with all positions 1-12.
                 Format: {"1": "labware_code", "2": None, ..., "12": "trash_code"}
                 Unassigned positions return None.
            
        Example:
            config = {
                1: "ablelabs_tip_box_200",        # Tip box at position 1 (int key)
                "2": "nest_12_reservoir_360102",  # Reservoir at position 2 (str key)  
                3: "spl_96_well_plate_30096",     # 96-well plate at position 3
                12: "ablelabs_trash"              # Trash at position 12
            }
            
            # Returns all 12 positions:
            {
                "1": "ablelabs_tip_box_200",
                "2": "nest_12_reservoir_360102", 
                "3": "spl_96_well_plate_30096",
                "4": None,
                ...
                "12": "ablelabs_trash"
            }
            
        Note:
            - Position keys can be strings or integers (both accepted)
            - Positions must be in range 1-12
            - Labware codes must exist in the labware library
            - Invalid labware codes will cause API errors
            - Empty positions should be omitted from input (will return None)
        """
        return await self._post("/api/v1/config/deck/", body=config)