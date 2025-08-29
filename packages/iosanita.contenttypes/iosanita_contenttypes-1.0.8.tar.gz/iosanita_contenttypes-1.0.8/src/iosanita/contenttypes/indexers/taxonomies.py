# -*- coding: utf-8 -*-
from collective.taxonomy import PATH_SEPARATOR
from collective.taxonomy.interfaces import ITaxonomy
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from zope.component import getSiteManager
from zope.globalrequest import getRequest


def get_taxonomy_vocab(field):
    request = getRequest()
    sm = getSiteManager()
    utility = sm.queryUtility(ITaxonomy, name=f"collective.taxonomy.{field}")
    if not utility:
        return None
    return utility.makeVocabulary(request.get("LANGUAGE"))


def extract_taxonomies(context, field, only_leaf=False):
    taxonomy_voc = get_taxonomy_vocab(field)
    if not taxonomy_voc:
        return []
    data = []
    value = getattr(context, field, []) or []
    if not isinstance(value, list):
        value = [value]
    for key in value:
        taxonomy_value = taxonomy_voc.inv_data.get(key, None)
        if not taxonomy_value:
            continue
        if taxonomy_value.startswith(PATH_SEPARATOR):
            taxonomy_value = taxonomy_value.replace(PATH_SEPARATOR, "", 1)

        if only_leaf:
            data.append(
                {"title": taxonomy_value.split(PATH_SEPARATOR)[-1], "token": key}
            )
        else:
            data.append(
                {"title": taxonomy_value.replace(PATH_SEPARATOR, "", 1), "token": key}
            )
    return data


@indexer(IDexterityContent)
def parliamo_di_metadata(context, **kw):
    """ """
    return extract_taxonomies(context=context, field="parliamo_di")


@indexer(IDexterityContent)
def a_chi_si_rivolge_tassonomia_metadata(context, **kw):
    """ """
    return extract_taxonomies(context=context, field="a_chi_si_rivolge_tassonomia")


@indexer(IDexterityContent)
def incarico_metadata(context, **kw):
    """ """
    return extract_taxonomies(context=context, field="incarico", only_leaf=True)


@indexer(IDexterityContent)
def tipologia_notizia_metadata(context, **kw):
    """ """
    return extract_taxonomies(
        context=context, field="tipologia_notizia", only_leaf=True
    )


@indexer(IDexterityContent)
def tipologia_servizio_metadata(context, **kw):
    """ """
    return extract_taxonomies(
        context=context, field="tipologia_servizio", only_leaf=True
    )
