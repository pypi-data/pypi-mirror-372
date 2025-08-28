# -*- coding: utf-8 -*-

from collective.behavior.talcondition import _
from collective.behavior.talcondition.utils import evaluateExpressionFor
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implementer


class ITALCondition(model.Schema):

    form.widget("tal_condition", size=80)
    tal_condition = schema.TextLine(
        title=_(u"TAL condition expression"),
        description=_(
            u"Enter a TAL expression that once evaluated "
            "will return 'True' if content should be "
            "available. Elements 'member', 'context' "
            "and 'portal' are available for the "
            "expression."
        ),
        required=False,
        default=u"",
    )

    form.widget(
        "roles_bypassing_talcondition",
        CheckBoxFieldWidget,
        multiple="multiple",
        size=15,
    )
    roles_bypassing_talcondition = schema.Set(
        title=_(u"Roles that will bypass the TAL condition"),
        description=_(
            u"Choose the different roles for which the TAL "
            "condition will not be evaluated and always "
            "considered 'True'."
        ),
        required=False,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Roles"),
    )

    def evaluate(self):
        """Evaluate the condition and returns True or False."""


alsoProvides(ITALCondition, IFormFieldProvider)


@implementer(ITALCondition)
class TALCondition(object):
    """ """

    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def get_tal_condition(self):
        return getattr(self.context, "tal_condition", "")

    def set_tal_condition(self, value):
        self.context.tal_condition = value

    tal_condition = property(get_tal_condition, set_tal_condition)

    def get_roles_bypassing_talcondition(self):
        return getattr(self.context, "roles_bypassing_talcondition", [])

    def set_roles_bypassing_talcondition(self, value):
        self.context.roles_bypassing_talcondition = value

    roles_bypassing_talcondition = property(
        get_roles_bypassing_talcondition, set_roles_bypassing_talcondition
    )

    def complete_extra_expr_ctx(self, extra_expr_ctx):
        """Complete extra_expr_ctx, this is made to be overrided."""
        return extra_expr_ctx

    def evaluate(self, extra_expr_ctx={}):
        extra_expr_ctx = self.complete_extra_expr_ctx(extra_expr_ctx)
        return evaluateExpressionFor(self, extra_expr_ctx=extra_expr_ctx)
