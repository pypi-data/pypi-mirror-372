import pytest

from kognic.io.util import deprecated_parameter


def test_deprecated_parameter_works_with_new_params():
    @deprecated_parameter("baz", "foo")
    def fun(foo: str, bar: str):
        pass

    fun("foo", "bar")
    fun(foo="foo", bar="bar")
    assert True


def test_deprecated_parameter_emits_warning():
    @deprecated_parameter("baz", "foo")
    def fun(foo: str, bar: str):
        pass

    with pytest.warns(DeprecationWarning) as record:
        fun(baz="foo", bar="bar")

    assert len(record) == 1
    assert str(record[0].message) == """The parameter "baz" has been deprecated in favor of "foo" and will be removed in the future"""


def test_chained_deprecated_parameter_emits_warnings():
    @deprecated_parameter("baz", "foo")
    @deprecated_parameter("qux", "bar")
    def fun(foo: str, bar: str):
        pass

    with pytest.warns(DeprecationWarning) as record:
        fun(baz="foo", qux="bar")

    assert len(record) == 2
    assert str(record[0].message) == """The parameter "baz" has been deprecated in favor of "foo" and will be removed in the future"""
    assert str(record[1].message) == """The parameter "qux" has been deprecated in favor of "bar" and will be removed in the future"""
