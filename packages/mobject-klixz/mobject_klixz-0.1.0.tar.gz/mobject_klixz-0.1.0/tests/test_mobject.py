
from mobject import MObject


def test_set_nested_properties():
    class A(MObject):
        _test_k: str = ""
        @property
        def Test(self):
            return self._test_k
        @Test.setter
        def Test(self, val: str):
            self._test_k = val

    a = A(Test="init")
    a.set_nested_property(['Test'], "setted")


test_set_nested_properties()