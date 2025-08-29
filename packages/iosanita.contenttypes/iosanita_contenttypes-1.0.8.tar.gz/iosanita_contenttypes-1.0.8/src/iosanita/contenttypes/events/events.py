from Acquisition import aq_inner
from Acquisition import aq_parent


def EventModified(dx_event, event):
    parent = aq_parent(aq_inner(dx_event))
    if not parent:
        return
    if parent.portal_type == "Event":
        parent.reindexObject(idxs=["rassegna"])
    return
