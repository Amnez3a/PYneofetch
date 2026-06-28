def test_main():
    with patch("sys.argv", ["pyneofetch"]):
        main()
from unittest.mock import patch
from pyneofetch import (
    build_info_lines,
    desktop_info,
    get_cpu_model,
    get_cpu_temp,
    get_package_count,
    main,
    other_info,
    pc_info,
    render,
    user_info,
)


def test_get_cpu_model():
    result = get_cpu_model()
    assert isinstance(result, str)
    assert result.strip() != ""


def test_get_cpu_temp():
    result = get_cpu_temp()
    assert isinstance(result, str)


def test_get_package_count():
    result = get_package_count()
    assert isinstance(result, str)


def test_get_pc_info():
    result = pc_info()
    assert isinstance(result, list)
    assert any("OS:" in line for line in result)
    assert any("Kernel:" in line for line in result)
    assert any("CPU:" in line for line in result)
    assert any("GPU:" in line for line in result)
    assert any("Uptime:" in line for line in result)
    assert any("Packages:" in line for line in result)


def test_user_info():
    result = user_info()
    assert isinstance(result, list)
    assert any("User:" in line for line in result)


def test_desktop_info():
    result = desktop_info()
    assert isinstance(result, list)
    assert any("Shell:" in line for line in result)
    assert any("WM/DE:" in line for line in result)
    assert any("Term:" in line for line in result)
    assert any("Env:" in line for line in result)


def test_other_info():
    result = other_info()
    assert isinstance(result, list)
    assert len(result) == 1
    assert "Python:" in result[0]


def test_build_info_lines():
    result = build_info_lines()
    assert isinstance(result, list)
    assert len(result) > 0


def test_render(capsys):
    render("TestArt", ["Line 1", "Line 2"])
    captured = capsys.readouterr()
    assert "TestArt" in captured.out
    assert "Line 1" in captured.out


def test_main():
    with patch("sys.argv", ["pyneofetch"]):
        main()
