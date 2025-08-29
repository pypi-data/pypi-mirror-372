from .export_view import ExportViewDownload
from .export_view import ExportViewTraverser
from .export_view import IExportViewDownload
from .export_view import IExportViewTraverser
from copy import deepcopy
from iosanita.contenttypes import _
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJson
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)


class ISearchBlockTraverser(IExportViewTraverser):
    pass


@implementer(ISearchBlockTraverser)
class SearchBlockTraverser(ExportViewTraverser):
    pass


@implementer(IExportViewDownload)
class SearchBlockDownload(ExportViewDownload):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.block_id = None
        self.export_type = "csv"

    def publishTraverse(self, request, name):
        """
        e.g.
        .../it/bandi/avvisi/searchblock/@@download/1ebe022a.csv?portal_type=...
        """
        if self.block_id is None:
            if "." in name:
                self.block_id, self.export_type = name.split(".", 2)
            else:
                self.block_id = name
            # 1. Get the block from page
            context = self.context.context
            blocks = getattr(context, "blocks", {})
            block_data = deepcopy(blocks.get(self.block_id))
            if not block_data:
                raise NotFound(f"Block {self.block_id} not found")
            if block_data["@type"] not in ["search"]:
                raise NotFound(f"Block {self.block_id} not valid")
            self.block_data = block_data
        else:
            raise NotFound("Not found")
        return self

    def _query_from_searchtext(self):
        if self.request.form.get("search"):
            return [
                {
                    "i": "SearchableText",
                    "o": "plone.app.querystring.operation.string.contains",
                    "v": self.request.form["search"],
                }
            ]
        return []

    def _query_from_facets(self):
        query = []
        for facet in self.block_data.get("facets") or []:
            if "field" not in facet:
                logger.warning("invalid facet %s", facet)
                continue
            if facet["field"]["value"] in self.request.form:
                if self.request.form[facet["field"]["value"]] in ["null"]:
                    continue

                if not facet.get("type"):
                    # default
                    query.append(
                        {
                            "i": facet["field"]["value"],
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": self.request.form[facet["field"]["value"]],
                        }
                    )
                elif facet["type"] == "daterangeFacet":
                    daterange = self.request.form[facet["field"]["value"]].split(",")
                    if not daterange[0]:
                        daterange[0] = "1970-01-01"
                    if not daterange[1]:
                        daterange[1] = "2500-01-01"
                    query.append(
                        {
                            "i": facet["field"]["value"],
                            "o": "plone.app.querystring.operation.date.between",
                            "v": daterange,
                        }
                    )
                elif facet["type"] == "selectFacet" and not facet["multiple"]:
                    query.append(
                        {
                            "i": facet["field"]["value"],
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": self.request.form[facet["field"]["value"]],
                        }
                    )
                elif facet["type"] == "checkboxFacet" and not facet["multiple"]:
                    query.append(
                        {
                            "i": facet["field"]["value"],
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": self.request.form[facet["field"]["value"]],
                        }
                    )
                else:
                    logger.warning("DEBUG: filter %s not implemented", facet)
                    query.append(
                        {
                            "i": facet["field"]["value"],
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": self.request.form[facet["field"]["value"]],
                        }
                    )
        return query

    def get_data(self):
        """
        # 1. cercare il blocco in pagina (self.context.blocks)
        # 2. recuperare le colonne, i filtri base e l'ordinamento base
        # 3. sovrascrivere/aggiungere filtri e ordinamenti da querystring
        # 4. fare la ricerca
        # 5. fare export in csv/pdf a seconda del formato
        """
        # 2. Get columns, base filters and sorting
        columns = self.block_data.get("columns", [])

        query_data = self.block_data["query"]
        query = query_data["query"]
        sort_on = query_data.get("sort_on")
        sort_order = query_data.get("sort_order")

        # 3. Update/Add filters and sorting from query string
        for key, value in self.request.form.items():
            if key == "sort_on":
                sort_on = value
            elif key == "sort_order":
                sort_order = value
            # else:
            #     import pdb; pdb.set_trace()
            #     query[key] = value
        query += self._query_from_facets()
        query += self._query_from_searchtext()

        querybuilder_parameters = dict(
            query=query,
            brains=True,
            b_start=0,
            b_size=9999,
            # sort_on=sort_on,
            # sort_order=sort_order,
            # limit=limit,
        )
        if sort_on:
            querybuilder_parameters["sort_on"] = sort_on
        if sort_order:
            querybuilder_parameters["sort_order"] = sort_order

        context = self.context.context

        querybuilder = getMultiAdapter(
            (context, self.request), name="querybuilderresults"
        )

        # 4. Execute the search
        # catalog = self.context.portal_catalog
        # results = catalog(**query)
        try:
            results = querybuilder(**querybuilder_parameters)
        except KeyError:
            # This can happen if the query has an invalid operation,
            # but plone.app.querystring doesn't raise an exception
            # with specific info.
            raise BadRequest("Invalid query.")

        # XXX: potrebbe essere overkilling serializzare, forse basta la ricerca al
        #      catalogo
        # XXX: consideriamo però che senza usare il serializzatore un utente potrebbe
        #      chiedere qualsiasi atttributo degli oggetti, senza un controllo fine
        #      sullo schema
        if results:
            fullobjects = True
            self.request.form["b_size"] = 9999
            results = getMultiAdapter((results, self.request), ISerializeToJson)(
                fullobjects=fullobjects
            )
            for obj in results["items"]:
                yield [obj["title"]] + [obj.get(c["field"]) for c in columns]

    def get_columns(self, data):
        # Il titolo va aggiunto di default come prima colonna ?
        # anche la url ?
        columns = self.block_data.get("columns", [])
        return [{"key": "title", "title": _("Titolo")}] + [
            {"key": c["field"], "title": c["title"]} for c in columns
        ]

    @view.memoize
    def _get_querystring(self):
        # @querystring endpoint
        context = self.context.context
        registry = getUtility(IRegistry)
        reader = getMultiAdapter((registry, self.request), IQuerystringRegistryReader)
        reader.vocab_context = context
        result = reader()
        return result

    # TODO: valutare eventuale titolo impostato sul blocco
    # def pdf_title(self):

    pdf_description_as_html = True

    def pdf_description(self) -> str:
        query = []
        querystring_registry = self._get_querystring()
        searchtext = self._query_from_searchtext()
        if searchtext and searchtext[0].get("v"):
            # TODO: translate
            query.append(f"Ricerca per: {searchtext[0]['v']}")
        for facet in self.block_data.get("facets") or []:
            if "field" not in facet:
                logger.warning("invalid facet %s", facet)
                continue
            if facet["field"]["value"] in self.request.form:
                value = self.request.form[facet["field"]["value"]]
                if value in ["null"]:
                    continue
                # TODO: gestire campi particolari come: multipli, date, ...
                index = querystring_registry["indexes"].get(facet["field"]["value"])
                if index:
                    if "values" in index:
                        # TODO: per i valori multipli ?
                        # TODO: facciamo constraint o fallback come ora?
                        if value in index["values"] and index["values"][value].get(
                            "title"
                        ):
                            query.append(
                                f'{facet["field"]["label"]}: {index["values"][value]["title"]}'
                            )
                            continue
                query.append(f'{facet["field"]["label"]}: {value}')
        if query:
            # TODO: translate
            txt = "Filtri applicati:\n- " + ",\n- ".join(query)
            return convertWebIntelligentPlainTextToHtml(txt)
