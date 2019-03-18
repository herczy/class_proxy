import unittest

from class_proxy import wrap_with, reset_proxy_cache, proxy_of


class TestClassProxy(unittest.TestCase):
    def setUp(self):
        reset_proxy_cache()
        self.proxy_class = wrap_with(Base, BaseProxy)
        self.base = Base()
        self.instance = self.proxy_class(self.base, 1)

    def test_get_proxy_class_attributes(self):
        self.assertEqual(1, self.proxy_class.a)
        self.assertEqual(3, self.proxy_class.b)
        self.assertEqual(4, self.proxy_class.c)

    def test_set_proxy_class_attribute(self):
        self.proxy_class.a = 5

        self.assertEqual(5, self.proxy_class.a)

    def test_set_new_proxy_class_attribute(self):
        self.proxy_class.x = 100

        self.assertEqual(100, self.proxy_class.x)
        self.assertEqual(100, self.instance.x)

    def test_delete_proxy_class_attribute(self):
        del self.proxy_class.a

        self.assertRaises(AttributeError, lambda: self.proxy_class.a)

    def test_get_proxy_instance_attribute(self):
        self.assertEqual(1, self.instance.a)
        self.assertEqual(3, self.instance.b)
        self.assertEqual(4, self.instance.c)

    def test_set_proxy_instance_attribute(self):
        self.instance.a = 5

        self.assertEqual(5, self.instance.a)

    def test_set_new_proxy_instance_attribute(self):
        self.instance.x = 100

        self.assertEqual(100, self.instance.x)

    def test_delete_proxy_instance_attribute(self):
        del self.instance.a

        self.assertRaises(AttributeError, lambda: self.instance.a)

    def test_delete_new_proxy_instance_attribute(self):
        self.instance.x = 100
        del self.instance.x

        self.assertRaises(AttributeError, lambda: self.instance.x)

    def test_proxy_class_for_methods(self):
        self.assertIs(self.base, self.instance.get_base())
        self.assertIs(self.instance, self.instance.get_proxy())
        self.assertIs(self.instance, self.instance.get_self())

    def test_skip_default_object_attributes(self):
        self.assertEqual("str-proxy", str(self.instance))
        self.assertEqual("repr-base", repr(self.instance))

    def test_error_when_trying_to_wrap_wrong_object_type(self):
        self.assertRaises(TypeError, self.proxy_class, 0, 1)

    def test_proxy_classes_are_cached(self):
        proxy0 = wrap_with(Base, BaseProxy)
        proxy1 = wrap_with(Base, BaseProxy)

        self.assertIs(proxy0, proxy1)

    def test_overwrite_proxy_name_using_wrap_with(self):
        proxy = wrap_with(Base, BaseProxy, name="CustomName")

        self.assertEqual("CustomName", proxy.__name__)

    def test_overwrite_proxy_name_using_proxy_of(self):
        proxy = proxy_of(Base, name="CustomName")(BaseProxy)

        self.assertEqual("CustomName", proxy.__name__)


class Base(object):
    a = 1
    b = 2

    def get_self(self):
        return self

    def get_base(self):
        return self

    def __str__(self):
        return "str-base"

    def __repr__(self):
        return "repr-base"


class BaseProxy(object):
    b = 3
    c = 4

    def __init__(self, d):
        self.d = d

    def get_self(self):
        return self

    def get_proxy(self):
        return self

    def __str__(self):
        return "str-proxy"
