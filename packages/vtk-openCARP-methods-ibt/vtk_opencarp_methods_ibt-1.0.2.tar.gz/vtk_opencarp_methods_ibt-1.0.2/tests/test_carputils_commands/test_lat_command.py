from ...src.vtk_openCARP_methods_ibt.carputils_commands.lat_command import LATCommand


def test_lat_command_initialization_consistency():
    # Create initial command with all attributes
    initial_cmd = LATCommand(
        threshold=0.9,
        id_name="ACTs",
        positional_index=0,
        all_flag=0,
        measurand=0,
        mode=0
    )

    # Convert to command string and back to class
    cmd_str = initial_cmd.to_cmd()
    converted_cmd = LATCommand.create_from_cmd_list(cmd_str)

    # Check if all attributes are preserved
    assert initial_cmd.threshold == converted_cmd.threshold
    assert initial_cmd.id_name == converted_cmd.id_name
    assert initial_cmd.positional_index == converted_cmd.positional_index
    assert initial_cmd.all == converted_cmd.all
    assert initial_cmd.measurand == converted_cmd.measurand
    assert initial_cmd.mode == converted_cmd.mode

    # Check if all attributes are identical
    assert vars(initial_cmd) == vars(converted_cmd)
