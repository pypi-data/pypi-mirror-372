import pytest
from typing import List
from treeparse import argument, option, command, group, Chain


def test_argument_model():
    arg = argument(name="test", arg_type=int, help="Test arg")
    assert arg.name == "test"
    assert arg.arg_type == int


def test_option_model():
    opt = option(flags=["--test", "-t"], arg_type=str, help="Test option")
    assert opt.flags == ["--test", "-t"]
    assert opt.arg_type == str


def test_command_validation_success():
    def callback(arg1: int, opt1: str):
        pass

    cmd = command(
        name="test",
        callback=callback,
        arguments=[argument(name="arg1", arg_type=int)],
        options=[option(flags=["--opt1"], arg_type=str)],
    )
    cmd.validate()  # Should not raise


def test_command_validation_name_mismatch():
    def callback(arg1: int, opt2: str):
        pass

    cmd = command(
        name="test",
        callback=callback,
        arguments=[argument(name="arg1", arg_type=int)],
        options=[option(flags=["--opt1"], arg_type=str)],
    )
    with pytest.raises(ValueError) as exc:
        cmd.validate()
    assert "name mismatch" in str(exc.value)


def test_command_validation_type_mismatch():
    def callback(arg1: str):
        pass

    cmd = command(
        name="test", callback=callback, arguments=[argument(name="arg1", arg_type=int)]
    )
    with pytest.raises(ValueError) as exc:
        cmd.validate()
    assert "type mismatch" in str(exc.value)


def test_group_model():
    grp = group(name="test", subgroups=[], commands=[])
    assert grp.name == "test"


def test_command_validation_list_arg():
    def callback(words: List[str]):
        pass

    cmd = command(
        name="echo",
        callback=callback,
        arguments=[argument(name="words", nargs="*", arg_type=str)],
    )
    cmd.validate()  # Should not raise


def test_command_validation_list_option():
    def callback(tags: List[str]):
        pass

    cmd = command(
        name="tag",
        callback=callback,
        options=[option(flags=["--tags"], nargs="+", arg_type=str)],
    )
    cmd.validate()  # Should not raise


def test_command_validation_list_mismatch():
    def callback(words: str):
        pass

    cmd = command(
        name="echo",
        callback=callback,
        arguments=[argument(name="words", nargs="*", arg_type=str)],
    )
    with pytest.raises(ValueError) as exc:
        cmd.validate()
    assert "type mismatch" in str(exc.value)


def test_command_validation_choices_default():
    def callback(arg1: int):
        pass

    # Valid default
    cmd = command(
        name="test",
        callback=callback,
        arguments=[argument(name="arg1", arg_type=int, default=3, choices=[1, 2, 3])],
    )
    cmd.validate()  # Should not raise

    # Invalid default
    with pytest.raises(ValueError) as exc:
        cmd = command(
            name="test",
            callback=callback,
            arguments=[
                argument(name="arg1", arg_type=int, default=4, choices=[1, 2, 3])
            ],
        )
        cmd.validate()
    assert "Default value 4 not in choices [1, 2, 3]" in str(exc.value)


def test_command_validation_list_choices_default():
    def callback(args: List[int]):
        pass

    # Valid list default
    cmd = command(
        name="test",
        callback=callback,
        arguments=[
            argument(
                name="args", nargs="*", arg_type=int, default=[1, 2], choices=[1, 2, 3]
            )
        ],
    )
    cmd.validate()  # Should not raise

    # Invalid list default
    with pytest.raises(ValueError) as exc:
        cmd = command(
            name="test",
            callback=callback,
            arguments=[
                argument(
                    name="args",
                    nargs="*",
                    arg_type=int,
                    default=[1, 4],
                    choices=[1, 2, 3],
                )
            ],
        )
        cmd.validate()
    assert "Default value 4 not in choices [1, 2, 3]" in str(exc.value)


def test_command_validation_flag_with_choices():
    def callback(flag: bool):
        pass

    with pytest.raises(ValueError) as exc:
        cmd = command(
            name="test",
            callback=callback,
            options=[option(flags=["--flag"], is_flag=True, choices=[True, False])],
        )
        cmd.validate()
    assert "Choices not applicable for flag option '--flag'" in str(exc.value)


def test_option_dest_prefer_long():
    opt = option(flags=["-o", "--output"])
    assert opt.get_dest() == "output"


def test_option_dest_short_only():
    opt = option(flags=["-o"])
    assert opt.get_dest() == "o"


def test_option_dest_long_first():
    opt = option(flags=["--output", "-o"])
    assert opt.get_dest() == "output"


def test_option_dest_with_explicit_dest():
    opt = option(flags=["-o", "--output"], dest="outfile")
    assert opt.get_dest() == "outfile"


def test_option_dest_no_flags():
    opt = option(flags=[])
    with pytest.raises(ValueError):
        opt.get_dest()


def test_chain_validation():
    def cb1(a: int):
        pass

    def cb2(b: str):
        pass

    cmd1 = command(
        name="cmd1", callback=cb1, arguments=[argument(name="a", arg_type=int)]
    )
    cmd2 = command(
        name="cmd2", callback=cb2, arguments=[argument(name="b", arg_type=str)]
    )
    chain_obj = Chain(name="chain", chained_commands=[cmd1, cmd2])
    chain_obj.validate()  # Should not raise

    # Check generated help
    assert chain_obj.help == "cmd1 ➜ cmd2"

    # Check effective args
    assert len(chain_obj.effective_arguments) == 2
    assert chain_obj.effective_arguments[0].name == "a"
    assert chain_obj.effective_arguments[1].name == "b"


def test_chain_conflict():
    def cb1(a: int):
        pass

    def cb2(a: str):
        pass

    cmd1 = command(
        name="cmd1", callback=cb1, arguments=[argument(name="a", arg_type=int)]
    )
    cmd2 = command(
        name="cmd2", callback=cb2, arguments=[argument(name="a", arg_type=str)]
    )
    chain_obj = Chain(name="chain", chained_commands=[cmd1, cmd2])
    with pytest.raises(ValueError) as exc:
        _ = chain_obj.effective_arguments
    assert "Conflicting argument dest 'a'" in str(exc.value)
