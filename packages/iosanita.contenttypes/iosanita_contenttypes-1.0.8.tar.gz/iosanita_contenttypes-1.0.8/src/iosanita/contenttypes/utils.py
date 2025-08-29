# -*- coding: utf-8 -*-
from uuid import uuid4

import logging


logger = logging.getLogger(__name__)


def create_default_blocks(context):
    title_uuid = str(uuid4())
    context.blocks = {title_uuid: {"@type": "title"}}
    context.blocks_layout = {"items": [title_uuid]}
