import os
from tempfile import NamedTemporaryFile
from unittest import TestCase

from lofar_parameterset.parameterset import parameterset


class TestParameterSet(TestCase):
    def test_construction(self):
        p = parameterset({"foo": "bar"})

        self.assertIn("foo", p)
        self.assertEqual(p["foo"], "bar")

    def test_fromString(self):
        PARSET = """
        foo = bar
        a.b.c = 3
        """

        p = parameterset.fromString(PARSET)

        self.assertIn("foo", p)
        self.assertEqual(p["foo"], "bar")
        self.assertIn("a.b.c", p)
        self.assertIn(p["a.b.c"], "3")

    def test_fromFile(self):
        PARSET = """
        foo = bar
        a.b.c = 3
        """
        parset_file = NamedTemporaryFile(suffix=".parset", delete=False)
        try:
            with open(parset_file.name, "w") as f:
                f.write(PARSET)
            p = parameterset.fromFile(parset_file.name)
            self.assertIn("foo", p)
            self.assertEqual(p["foo"], "bar")
            self.assertIn("a.b.c", p)
            self.assertIn(p["a.b.c"], "3")
        finally:
            os.remove(parset_file.name)

    def test_str(self):
        p = parameterset({"foo": "bar", "a.b.c": 3})
        self.assertEqual("\n".join(["a.b.c=3", 'foo="bar"']), str(p))

    def test_str_quoted(self):
        p = parameterset({"single_quote": "'single'", "double_quote": '"double"'})
        self.assertEqual(
            "\n".join(["double_quote='\"double\"'", "single_quote=\"'single'\""]),
            str(p),
        )

    def test_makeSubset(self):
        PARSET = """
        one.a = 1
        one.b = 2
        two.a = 3
        two.b = 4
        two.c.d = 5
        """

        p = parameterset.fromString(PARSET)
        subset = p.makeSubset("one.", "only.")

        self.assertDictEqual({"only.a": "1", "only.b": "2"}, subset)

    def test_fullModuleName(self):
        p = parameterset({"a.b.c.d": "xxxx"})

        self.assertEqual("a.b.c.d", p.fullModuleName("d"))
        self.assertEqual("a.b.c", p.fullModuleName("b.c"))
        self.assertEqual("", p.fullModuleName("d.param"))

    def test_getBool(self):
        for value in ("tRuE", "T", "yEs", "Y", "1"):
            self.assertTrue(parameterset({"key": value}).getBool("key"))
            self.assertTrue(parameterset({"key": value.lower()}).getBool("key"))
            self.assertTrue(parameterset({"key": value.upper()}).getBool("key"))

        for value in ("fAlSe", "F", "nO", "N", "0"):
            self.assertFalse(parameterset({"key": value}).getBool("key"))
            self.assertFalse(parameterset({"key": value.lower()}).getBool("key"))
            self.assertFalse(parameterset({"key": value.upper()}).getBool("key"))

        self.assertTrue(parameterset({}).getBool("key", True))
        self.assertFalse(parameterset({}).getBool("key", False))

        for value in ("maybe", "11"):
            with self.assertRaises(ValueError):
                parameterset({"key": value}).getBool("key")

        with self.assertRaises(KeyError):
            parameterset({}).getBool("key")

    def test_getInt(self):
        p = parameterset({"foo": "42"})

        self.assertEqual(42, p.getInt("foo"))
        self.assertEqual(0, p.getInt("foo2", 0))

        with self.assertRaises(KeyError):
            _ = p.getInt("baz")

    def test_getDouble(self):
        p = parameterset({"foo": "3.14"})

        self.assertAlmostEqual(3.14, p.getDouble("foo"))
        self.assertAlmostEqual(0.0, p.getDouble("foo2", 0.0))

        with self.assertRaises(KeyError):
            _ = p.getDouble("baz")

    def test_getString(self):
        p = parameterset({"foo": "bar"})

        self.assertEqual("bar", p.getString("foo"))
        self.assertEqual("baz", p.getString("foo2", "baz"))
        self.assertRaises(KeyError, p.getString, "baz")

    def test_getBoolVector(self):
        PARSET = """
        key=[true, false, t, f, yes, no, y, n, 1, 0]
        """

        p = parameterset.fromString(PARSET)

        self.assertListEqual(
            [True, False, True, False, True, False, True, False, True, False],
            p.getBoolVector("key"),
        )
        self.assertWarns(UserWarning, p.getBoolVector, "key", expandable=True)

    def test_getIntVector(self):
        PARSET = """
        key=[1, 2, 3, 4]
        """
        p = parameterset.fromString(PARSET)

        self.assertListEqual([1, 2, 3, 4], p.getIntVector("key"))
        self.assertWarns(UserWarning, p.getIntVector, "key", expandable=True)

    def test_getDoubleVector(self):
        PARSET = """
        key=[1.1, 2.2, 3.3, 4.4]
        """

        p = parameterset.fromString(PARSET)

        for x, y in zip([1.1, 2.2, 3.3, 4.4], p.getDoubleVector("key")):
            self.assertAlmostEqual(x, y)
        self.assertWarns(UserWarning, p.getDoubleVector, "key", expandable=True)

    def test_getStringVector(self):
        PARSET = """
        quoted=['Xre','Xim','Yre','Yim']
        unquoted=[Xre, Xim, Yre, Yim]
        """

        p = parameterset.fromString(PARSET)

        self.assertListEqual(["Xre", "Xim", "Yre", "Yim"], p.getStringVector("quoted"))
        self.assertListEqual(
            ["Xre", "Xim", "Yre", "Yim"], p.getStringVector("unquoted")
        )
        self.assertWarns(UserWarning, p.getStringVector, "quoted", expandable=True)
