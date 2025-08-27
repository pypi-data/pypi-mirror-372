import pytest
import sys
import json
from typing import List
from treeparse import cli, command, argument, option, Chain, group


def test_cli_build_parser():
    app = cli(name="test", help="Test CLI")
    parser = app.build_parser()
    assert parser.prog == "test"


def test_cli_validation_error(capsys):
    def callback(arg1: int):
        pass

    cmd = command(
        name="test", callback=callback, arguments=[argument(name="arg2", arg_type=int)]
    )
    app = cli(name="test", commands=[cmd])
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "name mismatch" in captured.out


def test_cli_help_output(capsys):
    app = cli(name="test", help="Test CLI")
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Usage: test ...  (--json, -h, --help)" in captured.out


def test_cli_with_command():
    called = [False]

    def callback():
        called[0] = True

    cmd = command(name="cmd", callback=callback)
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "cmd"]
    app.run()
    assert called[0]


def test_show_types(capsys):
    app = cli(name="test", show_types=True)
    arg = argument(name="arg", arg_type=int)
    opt = option(flags=["--opt"], arg_type=str)

    def callback(arg: int, opt: str):
        pass

    cmd = command(name="cmd", arguments=[arg], options=[opt], callback=callback)
    app.commands.append(cmd)
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "[ARG, int]" in captured.out
    assert "--opt: str" in captured.out


def test_show_defaults(capsys):
    app = cli(name="test", show_defaults=True)
    opt = option(flags=["--opt"], arg_type=str, default="default_value")

    def callback(opt: str):
        pass

    cmd = command(name="cmd", options=[opt], callback=callback)
    app.commands.append(cmd)
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "(default: default_value)" in captured.out


def test_cli_json_output(capsys):
    app = cli(name="test", help="Test CLI")
    sys.argv = ["test", "--json"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    json_output = captured.out.strip()
    try:
        data = json.loads(json_output)
    except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")
    assert data["name"] == "test"
    assert data["help"] == "Test CLI"
    assert data["type"] == "cli"


def test_cli_list_arg():
    called = [False]
    captured_words = []

    def callback(words: List[str]):
        called[0] = True
        captured_words.extend(words)

    cmd = command(
        name="echo",
        callback=callback,
        arguments=[argument(name="words", nargs="*", arg_type=str)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "echo", "hello", "world"]
    app.run()
    assert called[0]
    assert captured_words == ["hello", "world"]


def test_cli_list_option():
    called = [False]
    captured_tags = []

    def callback(tags: List[str]):
        called[0] = True
        captured_tags.extend(tags)

    cmd = command(
        name="tag",
        callback=callback,
        options=[option(flags=["--tags"], nargs="+", arg_type=str)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "tag", "--tags", "tag1", "tag2"]
    app.run()
    assert called[0]
    assert captured_tags == ["tag1", "tag2"]


def test_cli_bool_arg():
    called = [False]
    captured_bool = None

    def callback(flag: bool):
        nonlocal captured_bool
        called[0] = True
        captured_bool = flag

    cmd = command(
        name="booltest",
        callback=callback,
        arguments=[argument(name="flag", arg_type=bool)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "booltest", "true"]
    app.run()
    assert called[0]
    assert captured_bool is True


def test_cli_list_bool_option():
    called = [False]
    captured_flags = []

    def callback(flags: List[bool]):
        called[0] = True
        captured_flags.extend(flags)

    cmd = command(
        name="listbool",
        callback=callback,
        options=[option(flags=["--flags"], nargs="+", arg_type=bool)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "listbool", "--flags", "true", "false"]
    app.run()
    assert called[0]
    assert captured_flags == [True, False]


def test_cli_flag_option():
    called = [False]
    captured_flag = None

    def callback(flag: bool):
        nonlocal captured_flag
        called[0] = True
        captured_flag = flag

    cmd = command(
        name="flagtest",
        callback=callback,
        options=[option(flags=["--flag", "-f"], is_flag=True)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "flagtest", "--flag"]
    app.run()
    assert called[0]
    assert captured_flag is True


def test_super_cli():
    called = [False]

    def callback():
        called[0] = True

    sub_cmd = command(name="subcmd", callback=callback)
    sub_app = cli(name="sub", help="Sub CLI", commands=[sub_cmd])
    super_app = cli(name="test_super", help="Super CLI", subgroups=[sub_app])
    sys.argv = ["test_super", "sub", "subcmd"]
    super_app.run()
    assert called[0]


def test_choices_option(capsys):
    called = [False]
    captured_level = None

    def callback(level: int):
        nonlocal captured_level
        called[0] = True
        captured_level = level

    cmd = command(
        name="set-level",
        callback=callback,
        options=[option(flags=["--level"], arg_type=int, choices=[2, 3, 4])],
    )
    app = cli(name="test", commands=[cmd], show_types=True)
    # Test valid choice
    sys.argv = ["test", "set-level", "--level", "3"]
    app.run()
    assert called[0]
    assert captured_level == 3
    # Test invalid choice
    sys.argv = ["test", "set-level", "--level", "5"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "invalid choice" in captured.out
    # Test help output
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "--level: int (2|3|4)" in captured.out


def test_choices_argument(capsys):
    called = [False]
    captured_choice = None

    def callback(choice: str):
        nonlocal captured_choice
        called[0] = True
        captured_choice = choice

    cmd = command(
        name="choose",
        callback=callback,
        arguments=[argument(name="choice", arg_type=str, choices=["a", "b", "c"])],
    )
    app = cli(name="test", commands=[cmd], show_types=True)
    # Test valid choice
    sys.argv = ["test", "choose", "b"]
    app.run()
    assert called[0]
    assert captured_choice == "b"
    # Test invalid choice
    sys.argv = ["test", "choose", "d"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "invalid choice" in captured.out
    # Test help output
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "[CHOICE, str (a|b|c)]" in captured.out


def test_default_against_choices():
    def callback(opt: int):
        pass

    # Valid default
    option(flags=["--opt"], arg_type=int, default=3, choices=[2, 3, 4])
    cmd = command(
        name="test",
        callback=callback,
        options=[option(flags=["--opt"], arg_type=int, default=3, choices=[2, 3, 4])],
    )
    app = cli(name="test", commands=[cmd])
    app._validate()  # Should not raise

    # Invalid default
    with pytest.raises(ValueError) as exc:
        cmd = command(
            name="test",
            callback=callback,
            options=[
                option(flags=["--opt"], arg_type=int, default=5, choices=[2, 3, 4])
            ],
        )
        app = cli(name="test", commands=[cmd])
        app._validate()
    assert "Default value 5 not in choices [2, 3, 4]" in str(exc.value)


def test_line_connect(capsys):
    app = cli(name="test", help="Test CLI with line connect", line_connect=True)

    def callback():
        pass

    cmd = command(name="cmd", help="A command with help", callback=callback)
    app.commands.append(cmd)
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "─" in captured.out  # Check for connector lines
    assert "A command with help" in captured.out


def test_line_connect_option(capsys):
    app = cli(name="test", line_connect=True)

    def callback(opt: str):
        pass

    opt = option(flags=["--opt"], arg_type=str, help="An option with help")
    cmd = command(name="cmd", options=[opt], callback=callback)
    app.commands.append(cmd)
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "─" in captured.out  # Check for connector in option
    assert "An option with help" in captured.out


def test_option_short_long_flag_order():
    captured_output = None

    def callback(output: str):
        nonlocal captured_output
        captured_output = output

    opt = option(flags=["-o", "--output"], arg_type=str)
    cmd = command(name="cmd", options=[opt], callback=callback)
    app = cli(name="test", commands=[cmd])

    # Validate should pass with 'output' as param name
    app._validate()  # Should not raise

    # Run with short flag
    sys.argv = ["test", "cmd", "-o", "file.txt"]
    app.run()
    assert captured_output == "file.txt"

    # Run with long flag
    sys.argv = ["test", "cmd", "--output", "file.txt"]
    app.run()
    assert captured_output == "file.txt"


def test_option_long_short_order():
    captured_output = None

    def callback(output: str):
        nonlocal captured_output
        captured_output = output

    opt = option(flags=["--output", "-o"], arg_type=str)
    cmd = command(name="cmd", options=[opt], callback=callback)
    app = cli(name="test", commands=[cmd])

    app._validate()  # Should not raise

    sys.argv = ["test", "cmd", "-o", "file.txt"]
    app.run()
    assert captured_output == "file.txt"

    sys.argv = ["test", "cmd", "--output", "file.txt"]
    app.run()
    assert captured_output == "file.txt"


def test_option_short_only():
    captured_output = None

    def callback(o: str):
        nonlocal captured_output
        captured_output = o

    opt = option(flags=["-o"], arg_type=str)
    cmd = command(name="cmd", options=[opt], callback=callback)
    app = cli(name="test", commands=[cmd])

    app._validate()  # Should not raise

    sys.argv = ["test", "cmd", "-o", "file.txt"]
    app.run()
    assert captured_output == "file.txt"


def test_option_name_mismatch_short_only():
    def callback(output: str):
        pass

    opt = option(flags=["-o"], arg_type=str)
    cmd = command(name="cmd", options=[opt], callback=callback)
    app = cli(name="test", commands=[cmd])

    with pytest.raises(ValueError) as exc:
        app._validate()
    assert "name mismatch" in str(exc.value)


def test_display_name_includes_py(capsys):
    app = cli(name="test.py", help="Test CLI")
    sys.argv = ["test.py", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Usage: test.py ...  (--json, -h, --help)" in captured.out
    assert app.display_name == "test.py"


def test_display_name_no_py():
    app = cli(name="test", help="Test CLI")
    assert app.display_name == "test"


def test_super_cli_with_py_name(capsys):
    called = [False]

    def callback():
        called[0] = True

    sub_cmd = command(name="subcmd", callback=callback)
    sub_app = cli(name="sub.py", help="Sub CLI", commands=[sub_cmd])
    super_app = cli(name="test_super", help="Super CLI", subgroups=[sub_app])

    # Check help output
    sys.argv = ["test_super", "--help"]
    with pytest.raises(SystemExit):
        super_app.run()
    captured = capsys.readouterr()
    assert "sub.py " in captured.out  # display_name with .py

    # Check execution
    sys.argv = ["test_super", "sub.py", "subcmd"]
    super_app.run()
    assert called[0]

    # Check invalid call without .py
    sys.argv = ["test_super", "sub", "subcmd"]
    with pytest.raises(SystemExit):
        super_app.run()
    captured = capsys.readouterr()
    assert "invalid choice" in captured.out


def test_help_with_arguments(capsys):
    def callback(name: str):
        pass

    cmd = command(
        name="greet",
        help="Greet someone.",
        arguments=[argument(name="name", arg_type=str)],
        callback=callback,
    )
    app = cli(name="test", commands=[cmd])

    sys.argv = ["test", "greet", "John", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Usage: test greet [ARGS...] ...  (--json, -h, --help)" in captured.out
    assert "Greet someone." in captured.out


def test_chain_execution():
    calls = []

    def cb1(a: int):
        calls.append(("cb1", a))

    def cb2(b: str):
        calls.append(("cb2", b))

    cmd1 = command(
        name="cmd1", callback=cb1, arguments=[argument(name="a", arg_type=int)]
    )
    cmd2 = command(
        name="cmd2", callback=cb2, arguments=[argument(name="b", arg_type=str)]
    )
    chain_obj = Chain(name="chain", chained_commands=[cmd1, cmd2])
    app = cli(name="test", commands=[chain_obj])

    sys.argv = ["test", "chain", "42", "hello"]
    app.run()
    assert calls == [("cb1", 42), ("cb2", "hello")]


def test_chain_help(capsys):
    def cb1():
        pass

    def cb2():
        pass

    cmd1 = command(name="cmd1", callback=cb1)
    cmd2 = command(name="cmd2", callback=cb2)
    chain_obj = Chain(name="chain", chained_commands=[cmd1, cmd2])
    app = cli(name="test", commands=[chain_obj])

    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "chain" in captured.out
    assert "cmd1 ➜ cmd2" in captured.out


def test_group_argument_propagation():
    called = [False]

    def callback(id: int, name: str):
        called[0] = True
        assert id == 123
        assert name == "test"

    add_cmd = command(
        name="add", callback=callback, arguments=[argument(name="name", arg_type=str)]
    )

    user_group = group(
        name="user", arguments=[argument(name="id", arg_type=int)], commands=[add_cmd]
    )

    app = cli(name="test", subgroups=[user_group])

    sys.argv = ["test", "user", "123", "add", "test"]
    app.run()
    assert called[0]


def test_group_argument_in_help(capsys):
    def callback(id: int, name: str):
        pass

    cmd = command(
        name="add", callback=callback, arguments=[argument(name="name", arg_type=str)]
    )

    g = group(
        name="user", arguments=[argument(name="id", arg_type=int)], commands=[cmd]
    )

    app = cli(name="test", subgroups=[g], show_types=True)

    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "user [ID, int]" in captured.out
