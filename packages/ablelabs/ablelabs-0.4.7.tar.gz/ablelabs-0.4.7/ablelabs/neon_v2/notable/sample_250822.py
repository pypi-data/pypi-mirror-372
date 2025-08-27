# python 3.10+

# Install the ablelabs package using "pip install ablelabs"
import asyncio
import subprocess
from ablelabs.neon_v2.notable import Notable, LEDColor, ZReference

NEON_EXE_PATH = r"C:\your_path\NOTABLE-Neon.exe"


async def launch_neon_server(exe_path: str = NEON_EXE_PATH, wait_seconds: int = 5):
    """
    Launch NOTABLE-Neon.exe server and wait for initialization.

    Prerequisites:
    1. Place 'resources' folder in the same directory as NOTABLE-Neon.exe
    2. Check COM port in Device Manager and verify resources/setup_data.toml [communication.port]
    3. Configure [env] is_online setting in setup_data.toml:
       - is_online = true: Connect to actual hardware (production mode)
       - is_online = false: Run server without hardware connection (simulation mode)

    Alternative execution methods:
    - Double-click NOTABLE-Neon.exe manually
    - Run via command line: NOTABLE-Neon.exe
    - Use Windows service or task scheduler

    The server provides:
    - REST API endpoints at http://localhost:7777
    - Interactive Swagger UI documentation at http://localhost:7777/docs
    - OpenAPI specification at http://localhost:7777/openapi.json
    - ReDoc documentation at http://localhost:7777/redoc

    Args:
        exe_path: Path to NOTABLE-Neon.exe (None for default path)
        wait_seconds: Seconds to wait for server initialization
    """
    print("Launching NOTABLE-Neon.exe server...")
    print("📁 Ensure 'resources' folder is in the same directory as the executable")
    print("🔌 Check COM port settings in Device Manager and setup_data.toml")
    print("🌐 Configure [env] is_online in setup_data.toml:")
    print("   - is_online = true: Production mode (connects to actual hardware)")
    print("   - is_online = false: Simulation mode (no hardware connection)")
    print("📖 Access API documentation at http://localhost:7777/docs after launch")

    try:
        # Launch Neon.exe server
        subprocess.Popen([exe_path])
        print(f"⏳ Waiting {wait_seconds} seconds for server initialization...")
        await asyncio.sleep(wait_seconds)
        print("✅ Server should now be running at http://localhost:7777")

    except FileNotFoundError:
        print(f"❌ NOTABLE-Neon.exe not found at: {exe_path}")
        print(
            "💡 Alternative: Launch NOTABLE-Neon.exe manually before running this script"
        )
        raise
    except Exception as e:
        print(f"❌ Failed to launch server: {e}")
        print("💡 Try launching NOTABLE-Neon.exe manually")
        raise


async def setup_notable_client(base_url: str = "http://localhost:7777"):
    """
    Create Notable API client and retrieve library information.

    Args:
        base_url: Notable server URL

    Returns:
        tuple: (notable_client, pipette_library, labware_library)
    """
    print("Setting up Notable API client...")
    notable = Notable(base_url)

    # Get available resources
    print("📚 Retrieving pipette and labware libraries...")
    pipette_library = await notable.resource.library.get_pipette()
    pipette_codes = list(pipette_library.keys())
    labware_library = await notable.resource.library.get_labware()
    labware_codes = {
        category: list(dict(labware_codes).keys())
        for category, labware_codes in labware_library.items()
    }

    print(f"Available pipette codes: {pipette_codes}")
    print(f"Available labware codes: {labware_codes}")

    return notable, pipette_library, labware_library


async def simple_example():
    """Simple liquid handling workflow - minimal setup for quick start."""
    print("=== Simple Version: Basic Liquid Handling ===")

    # Setup client
    notable, pipette_library, labware_library = await setup_notable_client()

    # Set LED to indicate ready
    await notable.driver.io.set_led_bar(
        color=LEDColor.GREEN,
        bright_percent=20,
        progress_percent=100,
        blink_time_ms=0,  # No blinking
    )

    # Configure pipettes and deck layout
    await notable.config.pipette.set_pipette(
        {
            "1": "8ch_200ul",
        }
    )
    await notable.config.deck.set_deck(
        {
            "9": "ablelabs_tip_box_200",  # Tip box
            "6": "nest_12_reservoir_360102",  # Reservoir
            "3": "spl_96_well_plate_30096",  # 96-well plate
            "12": "ablelabs_trash",  # Trash
        }
    )

    # Basic liquid handling workflow
    await notable.controller.upper_module.initialize()
    await notable.controller.upper_module.pick_up_tip(
        pipette_number=1,
        deck_number="9",
        well="A1",
    )

    # Aspirate from reservoir
    await notable.controller.upper_module.move_to(
        pipette_number=1,
        deck_number="6",
        well="A1",
        z_reference=ZReference.BOTTOM,
    )
    await notable.controller.upper_module.aspirate(
        pipette_number=1,
        volume=100.0,
    )

    # Dispense to plate
    await notable.controller.upper_module.move_to(
        pipette_number=1,
        deck_number="3",
        well="A1",
        z_reference=ZReference.BOTTOM,
    )
    await notable.controller.upper_module.dispense(
        pipette_number=1,
        volume=100.0,
    )
    await notable.controller.upper_module.blow_out(
        pipette_number=1,
    )

    await notable.controller.upper_module.drop_tip(
        pipette_number=1,
        deck_number="12",
    )

    print("✓ Simple liquid handling completed!")


async def complex_example():
    """Complex liquid handling workflow - multiple transfers with different volumes."""
    print("=== Complex Version: Multiple Transfers ===")

    # Setup client
    notable, pipette_library, labware_library = await setup_notable_client()

    # Set LED to indicate ready
    await notable.driver.io.set_led_bar(
        color=LEDColor.WHITE,
        bright_percent=20,
        progress_percent=100,
        blink_time_ms=0,  # No blinking
    )

    pipette_number = 1
    pipette_code = "8ch_200ul"
    trash_deck_number = 12
    tip_deck_number = 9
    tip_labware_code = "ablelabs_tip_box_200"
    source_deck_number = 6
    target_deck_number = 3
    target_wells = [f"A{column}" for column in range(1, 13)]
    volume = 20.0
    flow_rate = 100
    withdraw_tip_z_speed = 20

    # Configure pipettes and deck layout
    await notable.config.pipette.set_pipette(
        {
            pipette_number: pipette_code,
        }
    )
    await notable.config.deck.set_deck(
        {
            tip_deck_number: tip_labware_code,  # Tip box
            source_deck_number: "nest_12_reservoir_360102",  # Reservoir
            target_deck_number: "spl_96_well_plate_30096",  # 96-well plate
            trash_deck_number: "ablelabs_trash",  # Trash
        }
    )

    def _chunk_list(lst: list[str], chunk_size: int) -> list[list[str]]:
        """Split a list into chunks of specified size."""
        return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

    # Calculate optimal chunk size for multi-dispense operations
    # Use minimum of pipette working volume and tip capacity to determine max volume per aspirate
    pipette = pipette_library[pipette_code]
    tip_labware = labware_library["tip_box"][tip_labware_code]
    tip = tip_labware["tip_info"]
    max_volume = min(pipette["working_volume"], tip["volume"])  # Safety constraint
    chunk_size = int(
        max_volume // volume
    )  # Number of wells that can be dispensed per aspirate
    chunked_wells = _chunk_list(
        target_wells, chunk_size
    )  # Group wells for batch processing

    print(
        ", ".join(
            [
                f"Complex Version: Multi-Dispense",
                f"pipette=({pipette_number}, {pipette_code})",
                f"tip=({tip_deck_number}, {tip_labware_code})",
                f"source={source_deck_number}",
                f"target={target_deck_number}",
                f"target_wells={target_wells}",
                f"volume={volume}",
                f"chunk_size={chunk_size}",
                f"chunked_wells={chunked_wells}",
            ]
        )
    )

    # Initialize robot and start liquid handling workflow
    await notable.driver.io.set_led_bar(
        color=LEDColor.BLUE,
        blink_time_ms=1000,  # Indicate initialization in progress
    )
    await notable.controller.upper_module.initialize(
        move_to_ready=False,  # Don't move to ready position to save time
    )
    await notable.driver.io.set_led_bar(
        color=LEDColor.GREEN,
        blink_time_ms=0,
        progress_percent=0,
    )

    # Pick up tips from the first position
    await notable.controller.upper_module.pick_up_tip(
        pipette_number=pipette_number,
        deck_number=tip_deck_number,
        well="A1",
    )

    # Update progress indicator (tip pickup counts as first step)
    n = len(chunked_wells) + 1  # +1 for tip pickup step
    await notable.driver.io.set_led_bar(
        progress_percent=int(100 * 1 / n),
    )

    # Process each chunk of wells
    for i, wells in enumerate(chunked_wells):
        print(
            f"--- Transfer {i+1}/{len(chunked_wells)}: {volume}μL to {len(wells)} wells ---"
        )

        # Pre-wet tip on first iteration for accuracy
        if i == 0:
            await notable.controller.upper_module.move_to(
                pipette_number=pipette_number,
                deck_number=source_deck_number,
                well="A1",
                z_reference=ZReference.BOTTOM,
                z_speed=True,
            )
            await notable.controller.upper_module.mix(
                pipette_number=pipette_number,
                cycle=3,
                volume=[volume] * len(wells),
                flow_rate=flow_rate,
            )
            await notable.controller.upper_module.blow_out(
                pipette_number=pipette_number,
            )
            await notable.controller.upper_module.move_z(
                pipette_number=pipette_number,
                deck_number=source_deck_number,
                z_reference=ZReference.TOP,
                z_speed=withdraw_tip_z_speed,
            )
            await notable.controller.upper_module.ready_plunger(
                pipette_number=pipette_number,
            )

        # Aspirate liquid from source reservoir
        await notable.controller.upper_module.move_to(
            pipette_number=pipette_number,
            deck_number=source_deck_number,
            well="A1",
            z_reference=ZReference.BOTTOM,
            z_speed=True,
        )
        await notable.controller.upper_module.aspirate(
            pipette_number=pipette_number,
            volume=[volume]
            * len(wells),  # aspirate for multi-well dispense: one volume per well
            flow_rate=flow_rate,
            pause_sec=0.5,  # Pause for liquid settling
        )
        await notable.controller.upper_module.move_z(
            pipette_number=pipette_number,
            deck_number=source_deck_number,
            z_reference=ZReference.TOP_JUST,
            z_speed=withdraw_tip_z_speed,
        )

        # Dispense to target wells sequentially
        for well in wells:
            await notable.controller.upper_module.move_to(
                pipette_number=pipette_number,
                deck_number=target_deck_number,
                well=well,
                z_reference=ZReference.BOTTOM,
                xyz_offset=[0, 0, 2],
                z_speed=True,
            )
            await notable.controller.upper_module.dispense(
                pipette_number=pipette_number,
                volume=volume,  # Single well dispense
                flow_rate=flow_rate,
                pause_sec=0.5,  # Pause for complete dispensing
            )
            await notable.controller.upper_module.move_z(
                pipette_number=pipette_number,
                deck_number=target_deck_number,
                z_reference=ZReference.TOP_JUST,
                z_speed=withdraw_tip_z_speed,
            )

        # Blow out any remaining liquid back to source reservoir
        await notable.controller.upper_module.move_to(
            pipette_number=pipette_number,
            deck_number=source_deck_number,
            well="A1",
            z_reference=ZReference.BOTTOM,
            xyz_offset=[0, 0, 2],
            z_speed=True,
        )
        await notable.controller.upper_module.blow_out(
            pipette_number=pipette_number,
        )
        await notable.controller.upper_module.move_z(
            pipette_number=pipette_number,
            deck_number=source_deck_number,
            z_reference=ZReference.TOP_JUST,
            z_speed=withdraw_tip_z_speed,
        )
        # Ready plunger for next iteration (if any)
        await notable.controller.upper_module.ready_plunger(
            pipette_number=pipette_number,
        )

        # Update progress indicator
        await notable.driver.io.set_led_bar(
            progress_percent=int(100 * (i + 2) / n),
        )

    # Drop tips to trash when all transfers are complete
    await notable.controller.upper_module.drop_tip(
        pipette_number=pipette_number,
    )

    # Final LED indication
    await notable.driver.io.set_led_bar(
        color=LEDColor.WHITE,
        progress_percent=100,
    )

    print("✓ Complex liquid handling completed!")


async def main():
    """
    Main function to run both simple and complex examples.

    You can modify this to run only the example you need:
    - await simple_example()     # Basic liquid handling
    - await complex_example()    # Multi-well transfer with optimization
    """
    print("NOTABLE Robot Liquid Handling Examples")
    print("=" * 40)

    # Launch server once for both examples (efficiency)
    await launch_neon_server()

    # Run examples sequentially
    await simple_example()
    await complex_example()

    print("\n🎉 All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
