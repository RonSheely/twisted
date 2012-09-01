# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for the subset of L{twisted.python.util} which has been ported to Python 3.
"""

from __future__ import division, absolute_import

import sys

from twisted.python.compat import _PY3
# Replace with trial as part of #5885:
if _PY3:
    from unittest import TestCase
else:
    from twisted.trial.unittest import SynchronousTestCase as TestCase

from twisted.python import _utilpy3 as util


class Record(util.FancyEqMixin):
    """
    Trivial user of L{FancyEqMixin} used by tests.
    """
    compareAttributes = ('a', 'b')

    def __init__(self, a, b):
        self.a = a
        self.b = b



class DifferentRecord(util.FancyEqMixin):
    """
    Trivial user of L{FancyEqMixin} which is not related to L{Record}.
    """
    compareAttributes = ('a', 'b')

    def __init__(self, a, b):
        self.a = a
        self.b = b



class DerivedRecord(Record):
    """
    A class with an inheritance relationship to L{Record}.
    """



class EqualToEverything(object):
    """
    A class the instances of which consider themselves equal to everything.
    """
    def __eq__(self, other):
        return True


    def __ne__(self, other):
        return False



class EqualToNothing(object):
    """
    A class the instances of which consider themselves equal to nothing.
    """
    def __eq__(self, other):
        return False


    def __ne__(self, other):
        return True



class EqualityTests(TestCase):
    """
    Tests for L{FancyEqMixin}.
    """
    def test_identity(self):
        """
        Instances of a class which mixes in L{FancyEqMixin} but which
        defines no comparison attributes compare by identity.
        """
        class Empty(util.FancyEqMixin):
            pass

        self.assertFalse(Empty() == Empty())
        self.assertTrue(Empty() != Empty())
        empty = Empty()
        self.assertTrue(empty == empty)
        self.assertFalse(empty != empty)


    def test_equality(self):
        """
        Instances of a class which mixes in L{FancyEqMixin} should compare
        equal if all of their attributes compare equal.  They should not
        compare equal if any of their attributes do not compare equal.
        """
        self.assertTrue(Record(1, 2) == Record(1, 2))
        self.assertFalse(Record(1, 2) == Record(1, 3))
        self.assertFalse(Record(1, 2) == Record(2, 2))
        self.assertFalse(Record(1, 2) == Record(3, 4))


    def test_unequality(self):
        """
        Unequality between instances of a particular L{record} should be
        defined as the negation of equality.
        """
        self.assertFalse(Record(1, 2) != Record(1, 2))
        self.assertTrue(Record(1, 2) != Record(1, 3))
        self.assertTrue(Record(1, 2) != Record(2, 2))
        self.assertTrue(Record(1, 2) != Record(3, 4))


    def test_differentClassesEquality(self):
        """
        Instances of different classes which mix in L{FancyEqMixin} should not
        compare equal.
        """
        self.assertFalse(Record(1, 2) == DifferentRecord(1, 2))


    def test_differentClassesInequality(self):
        """
        Instances of different classes which mix in L{FancyEqMixin} should
        compare unequal.
        """
        self.assertTrue(Record(1, 2) != DifferentRecord(1, 2))


    def test_inheritedClassesEquality(self):
        """
        An instance of a class which derives from a class which mixes in
        L{FancyEqMixin} should compare equal to an instance of the base class
        if and only if all of their attributes compare equal.
        """
        self.assertTrue(Record(1, 2) == DerivedRecord(1, 2))
        self.assertFalse(Record(1, 2) == DerivedRecord(1, 3))
        self.assertFalse(Record(1, 2) == DerivedRecord(2, 2))
        self.assertFalse(Record(1, 2) == DerivedRecord(3, 4))


    def test_inheritedClassesInequality(self):
        """
        An instance of a class which derives from a class which mixes in
        L{FancyEqMixin} should compare unequal to an instance of the base
        class if any of their attributes compare unequal.
        """
        self.assertFalse(Record(1, 2) != DerivedRecord(1, 2))
        self.assertTrue(Record(1, 2) != DerivedRecord(1, 3))
        self.assertTrue(Record(1, 2) != DerivedRecord(2, 2))
        self.assertTrue(Record(1, 2) != DerivedRecord(3, 4))


    def test_rightHandArgumentImplementsEquality(self):
        """
        The right-hand argument to the equality operator is given a chance
        to determine the result of the operation if it is of a type
        unrelated to the L{FancyEqMixin}-based instance on the left-hand
        side.
        """
        self.assertTrue(Record(1, 2) == EqualToEverything())
        self.assertFalse(Record(1, 2) == EqualToNothing())


    def test_rightHandArgumentImplementsUnequality(self):
        """
        The right-hand argument to the non-equality operator is given a
        chance to determine the result of the operation if it is of a type
        unrelated to the L{FancyEqMixin}-based instance on the left-hand
        side.
        """
        self.assertFalse(Record(1, 2) != EqualToEverything())
        self.assertTrue(Record(1, 2) != EqualToNothing())



class UnsignedIDTests(TestCase):
    """
    Tests for L{util.unsignedID} and L{util.setIDFunction}.
    """

    # Remove in #5885:
    def assertIdentical(self, a, b):
        """
        Assert the two arguments are the same object.
        """
        self.assertTrue(a is b)


    def setUp(self):
        """
        Save the value of L{util._idFunction} and arrange for it to be restored
        after the test runs.
        """
        self.addCleanup(setattr, util, '_idFunction', util._idFunction)


    def test_setIDFunction(self):
        """
        L{util.setIDFunction} returns the last value passed to it.
        """
        value = object()
        previous = util.setIDFunction(value)
        result = util.setIDFunction(previous)
        self.assertIdentical(value, result)


    def test_unsignedID(self):
        """
        L{util.unsignedID} uses the function passed to L{util.setIDFunction} to
        determine the unique integer id of an object and then adjusts it to be
        positive if necessary.
        """
        foo = object()
        bar = object()

        # A fake object identity mapping
        objects = {foo: 17, bar: -73}
        def fakeId(obj):
            return objects[obj]

        util.setIDFunction(fakeId)

        self.assertEqual(util.unsignedID(foo), 17)
        self.assertEqual(util.unsignedID(bar), (sys.maxsize + 1) * 2 - 73)


    def test_defaultIDFunction(self):
        """
        L{util.unsignedID} uses the built in L{id} by default.
        """
        obj = object()
        idValue = id(obj)
        if idValue < 0:
            idValue += (sys.maxsize + 1) * 2

        self.assertEqual(util.unsignedID(obj), idValue)