"""Containers module."""

import sys
import logging

from dependency_injector import containers, providers
from jinja2 import Environment, PackageLoader, select_autoescape
from tinydb import TinyDB
from simplegmail import Gmail

from .schemas import Settings
from .services import OANtfyService


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    logging = providers.Resource(
        logging.basicConfig,
        stream=sys.stdout,
        level=config.log.level,
        format=config.log.format,
    )

    jinja_env = providers.Resource(Environment, loader=PackageLoader("oa_ntfy"))

    db = providers.Resource(
        lambda config_path: TinyDB(config_path), config_path="db.json"
    )

    gmail = providers.Resource(Gmail)

    service = providers.Resource(
        OANtfyService,
        db=db,
        gmail=gmail,
        jinja_env=jinja_env,
        notification_format=config.ntfy.format,
        gmail_label_id=config.gmail.label_id,
        sleep_time=config.general.sleep_time,
        ntfy_topic_name=config.ntfy.topic_name,
        ntfy_protected_topic=config.ntfy.protected_topic,
        ntfy_bearer_token=config.ntfy.bearer_token,
        position_open_regex=config.general.position_open_regex,
        position_closed_regex=config.general.position_closed_regex,
        dry_run=config.general.dry_run,
    )
