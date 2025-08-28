.. image:: https://github.com/IMIO/collective.behavior.talcondition/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/IMIO/collective.behavior.talcondition/actions/workflows/main.yml

.. image:: https://coveralls.io/repos/collective/collective.behavior.talcondition/badge.png
  :target: https://coveralls.io/r/collective/collective.behavior.talcondition

.. image:: http://img.shields.io/pypi/v/collective.behavior.talcondition.svg
   :alt: PyPI badge
   :target: https://pypi.org/project/collective.behavior.talcondition


==========================================================================
collective.behavior.talcondition
==========================================================================

This package works for dexterity (behavior) and archetypes (schema extender).

It adds two fields on a content type or class:

* tal_condition : enter a `TAL expression <http://docs.zope.org/zope2/zope2book/AppendixC.html>`_ that once evaluated will return 'True' if content should be available. By default, elements 'member', 'context' and 'portal' are available for the expression but the TAL expression context may be extended using the 'extra_expr_ctx' parameter.

* roles_bypassing_talcondition : choose the different roles for which the TAL condition will not be evaluated and always considered \'True\'

It's then possible to use the 'evaluate' method to test the TAL condition.

How to use it
=============

For AT you have to provide the ITALConditionable on your class (see testing.zcml).

For DX you just have to activate the behavior on your content type.

Plone versions
==============
It has been developed and tested for Plone 4, 5, 6.


Translations
============

This product has been translated into

- French.

- Spanish.

You can contribute for any message missing or other new languages, join us at `Plone Collective Team <https://www.transifex.com/plone/plone-collective/>`_ into *Transifex.net* service with all world Plone translators community.

