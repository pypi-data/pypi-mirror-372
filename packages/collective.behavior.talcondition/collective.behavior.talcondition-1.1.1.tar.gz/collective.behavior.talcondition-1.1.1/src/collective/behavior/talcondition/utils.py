# -*- coding: utf-8 -*-

from AccessControl.class_init import InitializeClass
from collective.behavior.talcondition import PLONE_VERSION
from plone import api
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import createTrustedZopeEngine
from Products.PageTemplates.Expressions import SecureModuleImporter

import logging
import unittest


logger = logging.getLogger("collective.behavior.talcondition")
WRONG_TAL_CONDITION = (
    "The TAL expression '{0}' for element at '{1}' is wrong.  Original exception : {2}"
)


def evaluateExpressionFor(
    obj,
    extra_expr_ctx={},
    error_pattern=WRONG_TAL_CONDITION,
    raise_on_error=False,
    trusted=False,
):
    """Evaluate the expression stored in 'tal_condition' of given p_obj."""
    # get tal_condition
    tal_condition = obj.tal_condition and obj.tal_condition.strip() or ""

    roles_bypassing_talcondition = obj.roles_bypassing_talcondition

    if hasattr(obj, "context"):
        obj = obj.context
    return _evaluateExpression(
        obj,
        expression=tal_condition,
        roles_bypassing_expression=roles_bypassing_talcondition,
        extra_expr_ctx=extra_expr_ctx,
        error_pattern=error_pattern,
        raise_on_error=raise_on_error,
        trusted=trusted,
    )


def _evaluateExpression(
    obj,
    expression,
    roles_bypassing_expression=[],
    extra_expr_ctx={},
    empty_expr_is_true=True,
    error_pattern=WRONG_TAL_CONDITION,
    raise_on_error=False,
    trusted=False,
):
    """Evaluate given p_expression extending expression context with p_extra_expr_ctx."""
    if not expression or not expression.strip():
        return empty_expr_is_true

    res = True
    member = api.user.get_current()
    for role in roles_bypassing_expression or []:
        if member.has_role(str(role), obj):
            return res
    portal = api.portal.get()
    if trusted:
        ctx = createTrustedExprContext(obj.aq_inner.aq_parent, portal, obj)
        expr_handler = TrustedExpression
    else:
        ctx = createExprContext(obj.aq_inner.aq_parent, portal, obj)
        expr_handler = Expression
    ctx.setGlobal("member", member)
    ctx.setGlobal("context", obj)
    ctx.setGlobal("portal", portal)
    ctx.setGlobal('checkPermission', portal.portal_membership.checkPermission)

    for extra_key, extra_value in list(extra_expr_ctx.items()):
        ctx.setGlobal(extra_key, extra_value)

    if raise_on_error:
        res = expr_handler(expression)(ctx)
    else:
        try:
            res = expr_handler(expression)(ctx)
        except Exception as e:
            logger.warn(error_pattern.format(expression, obj.absolute_url(), str(e)))
            res = False
    return res


def createTrustedExprContext(folder, portal, object):
    """
    Expression evaluator trusted (not restricted python)
    Same as createExprContext but use the trusted engine.
    """
    pm = api.portal.get_tool("portal_membership")
    if object is None:
        object_url = ""
    else:
        object_url = object.absolute_url()
    if pm.isAnonymousUser():
        member = None
    else:
        member = pm.getAuthenticatedMember()
    data = {
        "object_url": object_url,
        "folder_url": folder.absolute_url(),
        "portal_url": portal.absolute_url(),
        "object": object,
        "folder": folder,
        "portal": portal,
        "nothing": None,
        "request": getattr(portal, "REQUEST", None),
        "modules": SecureModuleImporter,
        "member": member,
        "here": object,
    }
    return getTrustedEngine().getContext(data)


_trusted_engine = createTrustedZopeEngine()


def getTrustedEngine():
    """ """
    return _trusted_engine


class TrustedExpression(Expression):
    """ """

    text = ""
    _v_compiled = None

    def __init__(self, text):
        self.text = text
        if text.strip():
            self._v_compiled = getTrustedEngine().compile(text)

    def __call__(self, econtext):
        if not self.text.strip():
            return ""
        compiled = self._v_compiled
        if compiled is None:
            compiled = self._v_compiled = getTrustedEngine().compile(self.text)
        # ?? Maybe expressions should manipulate the security
        # context stack.
        res = compiled(econtext)
        if isinstance(res, Exception):
            raise res
        return res


InitializeClass(Expression)


@unittest.skipIf(PLONE_VERSION >= 5, "Archetypes extender skipped in Plone 5")
def applyExtender(portal, meta_types):
    """
    We add some fields using archetypes.schemaextender to every given p_meta_types.
    """
    logger.info(
        "Adding talcondition fields : updating the schema for meta_types %s"
        % ",".join(meta_types)
    )
    at_tool = api.portal.get_tool("archetype_tool")
    catalog = api.portal.get_tool("portal_catalog")
    catalog.ZopeFindAndApply(
        portal,
        obj_metatypes=meta_types,
        search_sub=True,
        apply_func=at_tool._updateObject,
    )
    logger.info("Done!")
