from plone import api

# import logging
# logger = logging.getLogger("imio.directory.policy")


def install_kimug(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runAllImportStepsFromProfile("profile-pas.plugins.kimug:default")
