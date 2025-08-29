import pytest


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4


def f():
    raise SystemExit(1)


def test_mytest():
    with pytest.raises(SystemExit):
        f()


def f2():
    raise ExceptionGroup(
        "Group message",
        [
            RuntimeError(),
        ],
    )


def test_exception_in_group():
    with pytest.raises(ExceptionGroup) as excinfo:
        f2()
    assert excinfo.group_contains(RuntimeError)
    assert not excinfo.group_contains(TypeError)
