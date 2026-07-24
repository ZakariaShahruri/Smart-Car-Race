from car_daemon import COMMANDS, resolve


def test_every_command_round_trips():
    for command, state in COMMANDS.items():
        assert resolve(command) == state


def test_unknown_command_defaults_to_stop():
    assert resolve("nonsense") == COMMANDS["stop"]


def test_stop_is_all_pins_low():
    assert resolve("stop") == (0, 0, 0, 0)


def test_forward_and_backward_are_opposite():
    lf, lb, rf, rb = resolve("forward")
    assert resolve("backward") == (lb, lf, rb, rf)


def test_spin_commands_drive_each_side_in_opposite_directions():
    lf, lb, rf, rb = resolve("spin-left")
    assert (lf, lb) != (rf, rb)
