from ablelabs.neon_v2.notable.core import Base


class Library(Base):
    """Resource library management for pipettes and labware.
    
    This class manages the robot's knowledge base of available pipettes and labware,
    including their physical dimensions, properties, and capabilities. Libraries are
    loaded from JSON files and can be updated or reloaded as needed.
    """

    async def get_pipette(self) -> dict:
        """Get pipette library information.
        
        Retrieves complete pipette library with specifications for all
        available pipette types including volume ranges, flow rates,
        and physical dimensions.
        
        Returns:
            dict: Pipette library mapping pipette codes to specifications.
                Format: {"pipette_code": {pipette_specs}, ...}
                
        Example:
            {
                "8ch_200ul": {
                    "name": "8-Channel 200μL",
                    "channels": 8,
                    "min_volume": 20,
                    "max_volume": 200,
                    "flow_rate": {"min": 1, "max": 500}
                }
            }
        """
        return await self._get("/api/v1/resource/library/pipette")

    async def update(self, pipette_code: str, data: dict) -> dict:
        """Update specific pipette library data.
        
        Modifies the specifications for a specific pipette type in the library.
        This allows customization of pipette parameters for specific applications.
        
        Args:
            pipette_code: Code identifying the pipette type to update
            data: Dictionary containing the updated pipette specifications
            
        Returns:
            dict: Confirmation of the library update
            
        Example:
            data = {
                "flow_rate": {"min": 5, "max": 300},  # Updated flow rate range
                "custom_offset": [0, 0, 2.5]          # Custom Z offset
            }
        """
        return await self._post(
            "/api/v1/resource/library/pipette/update",
            params={"pipette_code": pipette_code},
            body=data,
        )

    async def get_labware(self) -> dict:
        """Get labware library information.
        
        Retrieves complete labware library with specifications for all
        available labware types including dimensions, well layouts,
        and volume capacities.
        
        Returns:
            dict: Labware library organized by categories.
                Format: {"category": {"labware_code": {specs}, ...}, ...}
                
        Example:
            {
                "tip_box": {
                    "ablelabs_tip_box_200": {
                        "name": "ABLE Labs 200μL Tip Box",
                        "wells": 96,
                        "well_volume": 200
                    }
                },
                "well_plate": {
                    "spl_96_well_plate_30096": {
                        "name": "96-Well Plate",
                        "wells": 96,
                        "well_volume": 200
                    }
                }
            }
        """
        return await self._get("/api/v1/resource/library/labware")

    async def reload(self) -> dict:
        """Reload pipette and labware libraries from files.
        
        Forces a reload of both pipette and labware libraries from their
        respective JSON files. This is useful after manually editing library
        files or after software updates.
        
        Returns:
            dict: Reload status and any errors encountered
            
        Note:
            This operation may take several seconds to complete as it
            re-parses all library files and validates the data
        """
        return await self._post("/api/v1/resource/library/reload")
