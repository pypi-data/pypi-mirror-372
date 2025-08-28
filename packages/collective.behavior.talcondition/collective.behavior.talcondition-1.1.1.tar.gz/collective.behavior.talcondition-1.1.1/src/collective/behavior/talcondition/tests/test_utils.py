# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.behavior.talcondition import PLONE_VERSION
from collective.behavior.talcondition.behavior import ITALCondition
from collective.behavior.talcondition.interfaces import ITALConditionable
from collective.behavior.talcondition.testing import IntegrationTestCase
from collective.behavior.talcondition.utils import _evaluateExpression
from collective.behavior.talcondition.utils import applyExtender
from collective.behavior.talcondition.utils import evaluateExpressionFor
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from zope.interface import alsoProvides

import unittest


class TestUtils(IntegrationTestCase):

    def setUp(self):
        """ """
        super(TestUtils, self).setUp()
        # create a testitem
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(id='testitem',
                                  type_name='testtype',
                                  title='Test type')
        self.adapted = ITALCondition(self.portal.testitem)

    def test_wrong_condition(self):
        """In case the condition is wrong, it just returns False
           and a message is added to the Zope log."""
        # using a wrong expression does not break anything
        self.adapted.tal_condition = u'python: context.some_unexisting_method()'
        self.assertFalse(self.adapted.evaluate())

    @unittest.skipIf(PLONE_VERSION >= 5, 'Archetypes extender test skipped in Plone 5')
    def test_apply_extender(self):
        """Test that existing objects are correctly updated
           after enabling extender for their meta_type."""
        # the extender is not enabled for "Folder"
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(id='testfolder',
                                  type_name='Folder',
                                  title='Test folder')
        testfolder = self.portal.testfolder
        self.assertFalse(hasattr(testfolder, 'tal_condition'))
        self.assertFalse(ITALConditionable.providedBy(testfolder))
        # enable the extender for testfolder
        alsoProvides(testfolder, ITALConditionable)
        # the schema is not updated until we do it
        self.assertFalse(hasattr(testfolder, 'tal_condition'))
        applyExtender(self.portal, meta_types=('ATFolder', ))
        # now the field is available
        self.assertTrue(hasattr(testfolder, 'tal_condition'))

    def test_empty_condition(self):
        # using an empty expression is considered True
        self.adapted.tal_condition = None
        self.assertTrue(self.adapted.evaluate())

    def test_bypass_for_manager(self):
        """In this case, no matter the expression is False,
           it will return True if current user is 'Manager'."""
        # using a wrong expression does not break anything
        self.adapted.tal_condition = "python:False"
        self.assertFalse(evaluateExpressionFor(self.adapted))
        self.adapted.roles_bypassing_talcondition = [u'Manager']
        # as current user is Manager, he can bypass the expression result
        self.assertTrue(evaluateExpressionFor(self.adapted))

    def test_extra_expr_ctx(self):
        """It is possible to pass extra values that will be available
           in the context of the expression."""
        self.adapted.tal_condition = "python: value == '122'"
        self.assertFalse(evaluateExpressionFor(self.adapted))
        self.assertTrue(evaluateExpressionFor(self.adapted, {'value': '122'}))

    def test_base_expr_context(self):
        """Test the elements available by default in the expression."""
        self.assertEqual(_evaluateExpression(
            self.portal, expression='portal/getId'), 'plone')
        self.assertEqual(_evaluateExpression(
            self.portal, expression='member/getId'), TEST_USER_ID)
        self.assertEqual(_evaluateExpression(
            self.portal, expression='context/getPortalTypeName'), 'Plone Site')
        self.assertTrue(_evaluateExpression(
            self.portal, expression='python: checkPermission("View", portal)'))
        self.assertTrue(_evaluateExpression(
            self.portal,
            expression='python: checkPermission("Modify portal content", portal)'))
        logout()
        self.assertTrue(_evaluateExpression(
            self.portal, expression='python: checkPermission("View", portal)'))
        self.assertFalse(_evaluateExpression(
            self.portal,
            expression='python: checkPermission("Modify portal content", portal)'))

    def test_empty_expr_is_true(self):
        """Test parameter used by utils._evaluateExpression making an empty
           expression to be considered True or False."""
        # True by default
        self.assertTrue(_evaluateExpression(self.portal,
                                            expression=''))
        self.assertTrue(_evaluateExpression(self.portal,
                                            expression=None))
        self.assertFalse(_evaluateExpression(self.portal,
                                             expression='',
                                             empty_expr_is_true=False))
        self.assertFalse(_evaluateExpression(self.portal,
                                             expression=None,
                                             empty_expr_is_true=False))

    def test_raise_on_error(self):
        """By default, a wrong expression will return False, except if raise_on_error=True,
           in this case the exception will be raised."""
        self.adapted.tal_condition = u'python: context.some_unexisting_method()'
        self.assertFalse(evaluateExpressionFor(self.adapted))
        self.assertRaises(AttributeError, evaluateExpressionFor, self.adapted, raise_on_error=True)

    def test_trusted(self):
        self.assertRaises(Unauthorized,
                          _evaluateExpression,
                          self.portal,
                          expression='python: context.unrestrictedTraverse("view")',
                          raise_on_error=True)
        self.assertTrue(_evaluateExpression(
            self.portal,
            expression='python: context.unrestrictedTraverse("view")',
            raise_on_error=True,
            trusted=True))
