# -*- coding: utf-8 -*-
from collective.behavior.talcondition import PLONE_VERSION
from collective.behavior.talcondition.interfaces import ITALConditionable
from collective.behavior.talcondition.testing import IntegrationTestCase
from collective.behavior.talcondition.utils import evaluateExpressionFor
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME

import unittest


class TestExtender(IntegrationTestCase):

    @unittest.skipIf(PLONE_VERSION >= 5, 'Archetypes extender test skipped in Plone 5')
    def test_extender(self):
        """The extender is enabled on ATDocument in testing.zcml.
           Check that 'tal_condition' is available."""
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(id='doc',
                                  type_name='Document',
                                  title='Test document')
        doc = self.portal.doc
        self.assertTrue(ITALConditionable.providedBy(doc))
        # set a tal_condition and evaluate
        # this is True
        doc.tal_condition = u"python:context.portal_type=='Document'"
        self.assertTrue(evaluateExpressionFor(doc))
        # this is False
        doc.tal_condition = u"python:context.portal_type=='unexisting_portal_type'"
        self.assertFalse(evaluateExpressionFor(doc))
