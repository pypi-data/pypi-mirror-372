# -*- coding: utf-8 -*-
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from collective.behavior.talcondition.interfaces import ICollectiveBehaviorTalconditionLayer
from collective.behavior.talcondition.interfaces import ITALConditionable
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from zope.component import adapts
from zope.interface import implementer


class TALConditionStringField(ExtensionField, StringField):
    """A string field that will contain an eventual TAL condition expression."""


class TALConditionLinesField(ExtensionField, LinesField):
    """A Lines field that will contain all roles
       that will bypass the tal condition."""


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class TALConditionExtender(object):
    """TALCondition class"""

    adapts(ITALConditionable)

    layer = ICollectiveBehaviorTalconditionLayer

    fields = [
        TALConditionStringField(
            'tal_condition',
            required=False,
            default='',
            searchable=False,
            languageIndependent=True,
            widget=StringWidget(
                label=(u"TAL condition expression"),
                description=(u'Enter a TAL expression that once evaluated '
                             'will return \'True\' if content should be '
                             'available. Elements \'member\', \'context\' '
                             'and \'portal\' are available for the '
                             'expression.'),
                i18n_domain='collective.behavior.talcondition',
                size="80",
            ),
        ),
        TALConditionLinesField(
            'roles_bypassing_talcondition',
            required=False,
            searchable=False,
            languageIndependent=True,
            widget=MultiSelectionWidget(
                size=10,
                label=(u'Roles that will bypass the TAL condition'),
                description=(u'Choose the different roles for which the TAL '
                             'condition will not be evaluated and always '
                             'considered \'True\'.'
                             ),
                i18n_domain='collective.behavior.talcondition',
            ),
            enforceVocabulary=True,
            multiValued=1,
            vocabulary_factory='plone.app.vocabularies.Roles',
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
