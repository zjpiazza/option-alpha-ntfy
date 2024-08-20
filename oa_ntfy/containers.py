"""Containers module."""

from dependency_injector import containers, providers
from jinja2 import Environment, PackageLoader, select_autoescape
from tinydb import TinyDB
from simplegmail import Gmail

from .schemas import Settings
from .services import Service


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    jinja_env = providers.Resource(Environment, loader=PackageLoader("oa_ntfy"))

    db = providers.Resource(
        lambda config_path: TinyDB(config_path), config_path="db.json"
    )

    gmail = providers.Resource(Gmail)

    service = providers.Resource(
        Service,
        db=db,
        gmail=gmail,
        jinja_env=jinja_env,
        notification_format=config.notification_format,
        gmail_label_id=config.gmail_label_id,
        sleep_time=config.sleep_time,
        ntfy_topic_name=config.ntfy_topic_name,
        ntfy_protected_topic=config.ntfy_protected_topic,
        ntfy_bearer_token=config.ntfy_bearer_token,
        position_open_regex=config.position_open_regex,
        position_closed_regex=config.position_closed_regex,
        dry_run=config.dry_run,
    )
