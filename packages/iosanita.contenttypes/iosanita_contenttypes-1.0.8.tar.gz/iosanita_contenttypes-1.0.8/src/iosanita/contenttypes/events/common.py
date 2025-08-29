# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces import IIosanitaContenttypesLayer
from iosanita.contenttypes.utils import create_default_blocks
from plone import api
from Products.CMFPlone.interfaces import ISelectableConstrainTypes

import logging


logger = logging.getLogger(__name__)


SUBFOLDERS_MAPPING = {
    "ComeFarePer": {
        "content": [
            {"id": "allegati", "title": "Allegati", "allowed_types": ("File",)},
        ],
    },
    "Bando": {
        "content": [
            {
                "id": "graduatoria",
                "title": "Graduatoria",
                "type": "Bando Folder Deepening",
            },
            {
                "id": "altri-allegati",
                "title": "Altri allegati",
                "type": "Bando Folder Deepening",
            },
            {
                "id": "adempimenti-consequenziali",
                "title": "Adempimenti consequenziali",
                "type": "Bando Folder Deepening",
            },
        ],
    },
    "Documento": {
        "content": [
            {
                "id": "immagini",
                "title": "Immagini",
                "type": "Document",
                "allowed_types": ("Image", "Link"),
            },
        ],
    },
    "Event": {
        "content": [
            {
                "id": "immagini",
                "title": "Immagini",
                "allowed_types": ("Image", "Link"),
                "publish": True,
            },
            {
                "id": "video",
                "title": "Video",
                "allowed_types": ("Link",),
                "publish": True,
            },
            {
                "id": "sponsor-evento",
                "title": "Sponsor Evento",
                "allowed_types": ("Link",),
                "publish": True,
            },
            {
                "id": "allegati",
                "title": "Allegati",
                "allowed_types": ("File",),
                "publish": True,
            },
        ],
    },
    "News Item": {
        "content": [
            {
                "id": "immagini",
                "title": "Immagini",
                "allowed_types": ("Image", "Link"),
            },
            {
                "id": "video",
                "title": "Video",
                "allowed_types": ("Link",),
            },
            {
                "id": "allegati",
                "title": "Allegati",
                "allowed_types": ("File",),
            },
        ],
    },
    "Persona": {
        "content": [
            {
                "id": "curriculum-vitae",
                "title": "Curriculum vitae",
                "allowed_types": ("File",),
            },
            {
                "id": "immagini",
                "title": "Immagini",
                "allowed_types": ("Image", "Link"),
            },
            {
                "id": "video",
                "title": "Video",
                "allowed_types": ("Link",),
            },
            {
                "id": "allegati",
                "title": "Allegati",
                "allowed_types": ("File",),
            },
        ],
        "allowed_types": [],
    },
    "Servizio": {
        "content": [
            {
                "id": "modulistica",
                "title": "Modulistica",
                "allowed_types": (
                    "File",
                    "Link",
                ),
            },
            {
                "id": "allegati",
                "title": "Allegati",
                "allowed_types": ("File",),
            },
        ],
    },
    "UnitaOrganizzativa": {
        "content": [
            {"id": "allegati", "title": "Allegati", "allowed_types": ("File",)},
        ],
    },
    "Step": {
        "content": [
            {"id": "allegati", "title": "Allegati", "allowed_types": ("File",)},
        ],
    },
    "Struttura": {
        "content": [
            {"id": "allegati", "title": "Allegati", "allowed_types": ("File",)},
            {
                "id": "immagini",
                "title": "Immagini",
                "allowed_types": ("Image", "Link"),
            },
            {
                "id": "video",
                "title": "Video",
                "allowed_types": ("Link",),
            },
        ],
    },
}


def onModify(context, event):
    for description in event.descriptions:
        if "IBasic.title" in getattr(
            description, "attributes", []
        ) or "IDublinCore.title" in getattr(description, "attributes", []):
            context_state = api.content.get_view(
                name="plone_context_state", context=context, request=context.REQUEST
            )
            if context_state.is_folderish():
                for child in context.listFolderContents():
                    child.reindexObject(idxs=["parent"])


def createSubfolders(context, event):
    """
    Create subfolders structure based on a portal_type mapping
    """
    if not IIosanitaContenttypesLayer.providedBy(context.REQUEST):
        return

    subfolders_mapping = SUBFOLDERS_MAPPING.get(context.portal_type, [])
    if not subfolders_mapping:
        return

    for mapping in subfolders_mapping.get("content", {}):
        if mapping["id"] not in context.keys():
            portal_type = mapping.get("type", "Document")
            child = api.content.create(
                container=context,
                type=portal_type,
                title=mapping["title"],
                id=mapping["id"],
            )

            if portal_type == "Document":
                create_default_blocks(context=child)

            if portal_type in ["Folder", "Document", "Bando Folder Deepening"]:
                child.exclude_from_search = True
                child.reindexObject(idxs=["exclude_from_search"])
                if portal_type != "Bando Folder Deepening":
                    child.exclude_from_nav = True
                    child.reindexObject(idxs=["exclude_from_nav"])

            # select constraints
            if mapping.get("allowed_types", ()):
                constraints_child = ISelectableConstrainTypes(child)
                constraints_child.setConstrainTypesMode(1)
                constraints_child.setLocallyAllowedTypes(mapping["allowed_types"])

            if mapping.get("publish", False):
                with api.env.adopt_roles(["Reviewer"]):
                    api.content.transition(obj=child, transition="publish")

    allowed_types = subfolders_mapping.get("allowed_types", None)
    if allowed_types is not None and not isinstance(allowed_types, list):
        raise ValueError("Subfolder map is not well formed")

    if isinstance(allowed_types, list):
        constraints_context = ISelectableConstrainTypes(context)
        constraints_context.setConstrainTypesMode(1)
        constraints_context.setLocallyAllowedTypes(allowed_types)
