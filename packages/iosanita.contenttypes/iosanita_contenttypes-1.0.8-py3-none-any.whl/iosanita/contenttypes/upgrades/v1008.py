# -*- coding: utf-8 -*-


DEFAULT_PROFILE = "profile-iosanita.contenttypes:default"


def upgrade(context):
    """ """
    context.runImportStepFromProfile(
        DEFAULT_PROFILE, "plone.app.registry", run_dependencies=False
    )
