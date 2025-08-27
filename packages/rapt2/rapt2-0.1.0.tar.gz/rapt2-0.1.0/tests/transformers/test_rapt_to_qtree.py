from rapt2.rapt import Rapt

from rapt2.transformers.qtree.constants import *
from rapt2.treebrd.grammars.extended_grammar import ExtendedGrammar
from tests.transformers.test_transfomer import TestTransformer


class TestQTreeTransformer(TestTransformer):
    def setUp(self):
        self.translate = self.translate_func(Rapt(grammar="Extended Grammar").to_qtree)


class TestRelation(TestQTreeTransformer):
    def test_single_relation(self):
        ra = "alpha;"
        expected = [r"\Tree[.$alpha$ ]"]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = "alpha; beta;"
        expected = [r"\Tree[.$alpha$ ]", r"\Tree[.$beta$ ]"]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestSelect(TestQTreeTransformer):
    def test_simple(self):
        ra = r"\select_{a1=a2} alpha;"
        expected = [r"\Tree[.${}_{{a1 = a2}}$ [.$alpha$ ] ]".format(SELECT_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestProject(TestQTreeTransformer):
    def test_simple(self):
        ra = r"\project_{a1, a2, a3} alpha;"
        expected = [r"\Tree[.${}_{{a1, a2, a3}}$ [.$alpha$ ] ]".format(PROJECT_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestRename(TestQTreeTransformer):
    def test_rename_relation(self):
        ra = r"\rename_{Apex} alpha;"
        expected = [r"\Tree[.${}_{{apex(a1, a2, a3)}}$ [.$alpha$ ] ]".format(RENAME_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_attributes(self):
        ra = r"\rename_{(a, b, c)} alpha;"
        expected = [r"\Tree[.${}_{{alpha(a, b, c)}}$ [.$alpha$ ] ]".format(RENAME_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_relation_and_attributes(self):
        ra = r"\rename_{apex(a, b, c)} alpha;"
        expected = [r"\Tree[.${}_{{apex(a, b, c)}}$ [.$alpha$ ] ]".format(RENAME_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestAssignment(TestQTreeTransformer):
    def test_relation(self):
        ra = "new_alpha := alpha;"
        expected = [r"\Tree[.$new_alpha(a1,a2,a3)$ [.$alpha$ ] ]"]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_relation_with_attributes(self):
        ra = "new_alpha(a, b, c) := alpha;"
        expected = [r"\Tree[.$new_alpha(a,b,c)$ [.$alpha$ ] ]"]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestJoin(TestQTreeTransformer):
    def test_relation(self):
        ra = r"alpha \join beta;"
        expected = [r"\Tree[.${}$ [.$alpha$ ] [.$beta$ ] ]".format(JOIN_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestNaturalJoin(TestQTreeTransformer):
    grammar = ExtendedGrammar

    def test_relation(self):
        ra = r"alpha \natural_join beta;"
        expected = [r"\Tree[.${}$ [.$alpha$ ] [.$beta$ ] ]".format(NATURAL_JOIN_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestThetaJoin(TestQTreeTransformer):
    grammar = ExtendedGrammar

    def test_relation(self):
        ra = r"alpha \join_{a1 = b1} beta;"
        expected = [
            r"\Tree[.${}_{{a1 = b1}}$ [.$alpha$ ] [.$beta$ ] ]".format(THETA_JOIN_OP)
        ]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestUnion(TestQTreeTransformer):
    def test_simple(self):
        ra = r"gamma \union gammatwin;"
        expected = [r"\Tree[.${}$ [.$gamma$ ] [.$gammatwin$ ] ]".format(UNION_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestIntersect(TestQTreeTransformer):
    grammar = ExtendedGrammar

    def test_simple(self):
        ra = r"gamma \intersect gammatwin;"
        expected = [r"\Tree[.${}$ [.$gamma$ ] [.$gammatwin$ ] ]".format(INTERSECT_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestDifference(TestQTreeTransformer):
    def test_simple(self):
        ra = r"gamma \difference gammatwin;"
        expected = [r"\Tree[.${}$ [.$gamma$ ] [.$gammatwin$ ] ]".format(DIFFERENCE_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)
