import time
import logging
from .schemas import OATrade, OATradeClosed, OATradeOpened, NtfyNotification
from requests import post, HTTPError
from tinydb import TinyDB, Query
from simplegmail.message import Message as GmailMessage
from typing import List
from bs4 import BeautifulSoup, PageElement
import re
from simplegmail import Gmail

from jinja2 import Environment


from datetime import datetime


class OANtfyService:

    def __init__(
        self,
        db: TinyDB,
        gmail: Gmail,
        notification_format: str,
        jinja_env: Environment,
        gmail_label_id: str,
        sleep_time: float,
        ntfy_topic_name: str,
        ntfy_protected_topic: bool,
        ntfy_bearer_token: str,
        position_open_regex: str,
        position_closed_regex: str,
        dry_run: bool,
    ) -> None:
        self.db = db
        self.gmail = gmail
        self.notification_format = notification_format
        self.jinja_env = jinja_env
        self.gmail_label_id = gmail_label_id
        self.sleep_time = sleep_time
        self.ntfy_topic_name = ntfy_topic_name
        self.ntfy_protected_topic = ntfy_protected_topic
        self.ntfy_bearer_token = ntfy_bearer_token
        self.position_open_regex = position_open_regex
        self.position_closed_regex = position_closed_regex
        self.dry_run = dry_run

        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.logger.info("Scanning for new messages...")

        while True:
            messages = self.gmail.get_messages(labels=[self.gmail_label_id])
            for message in messages:
                self.process_email(message)

            self.logger.debug("Sleeping for %s seconds", self.sleep_time)
            time.sleep(self.sleep_time)

    def list_gmail_labels(self) -> None:
        name_width = 40
        id_width = 20

        # Print the header with the column widths
        print(f"{'Label Name':<{name_width}} {'Label ID':<{id_width}}")
        print("=" * (name_width + id_width))

        # Print each label in a formatted manner
        for label in self.gmail.list_labels():
            print(f"{label.name:<{name_width}} {label.id:<{id_width}}")

    def send_ntfy_notification(self, trade: OATrade):
        # Send request
        # TODO: Add retry handler
        notification = self.format_notification(trade)

        headers = {"Title": notification.title, "Markdown": "yes"}

        if self.ntfy_protected_topic:
            headers["Authorization"] = f"Bearer {self.ntfy_bearer_token}"
        if notification.format == "markdown":
            headers["Markdown"] = "yes"

        if self.dry_run:
            print(
                f"\n"
                f"{'-' * 80}\n"
                f"{notification.title}\n"
                f"\n"
                f"{notification.text}\n"
                f"{'-' * 80}"
            )
            return True

        try:
            response = post(
                f"https://ntfy.sh/{self.ntfy_topic_name}",
                data=notification.text,
                headers=headers,
            )
            response.raise_for_status()
            if response.ok:
                self.logger.info(trade)
                return True

        except HTTPError:
            return False

    def format_notification(self, trade: OATrade) -> NtfyNotification:

        if isinstance(trade, OATradeOpened):

            if self.notification_format == "plaintext":
                template = self.jinja_env.get_template("trade_opened.j2")
            elif self.notification_format == "markdown":
                template = self.jinja_env.get_template("trade_opened.md")
            else:
                raise ValueError("Unsupported notification format")

            return NtfyNotification(
                title=str(trade),
                text=template.render(
                    bot=trade.bot,
                    symbol=trade.symbol,
                    strategy=trade.strategy,
                    position=trade.position,
                    expiration=trade.expiration,
                    quantity=trade.quantity,
                    cost=trade.cost,
                    price=trade.price,
                ),
                format=self.notification_format,
            )
        elif isinstance(trade, OATradeClosed):

            if self.notification_format == "plaintext":
                template = self.jinja_env.get_template("trade_closed.j2")
            elif self.notification_format == "markdown":
                template = self.jinja_env.get_template("trade_closed.md")
            else:
                raise ValueError("Unsupported notification format")

            return NtfyNotification(
                title=str(trade),
                text=template.render(
                    bot=trade.bot,
                    symbol=trade.symbol,
                    strategy=trade.strategy,
                    position=trade.position,
                    expiration=trade.expiration,
                    quantity=trade.quantity,
                    close_price=trade.close_price,
                    profit_loss=trade.profit_loss,
                ),
                format=self.notification_format,
            )
        else:
            raise ValueError("Unsupported trade type")

    def process_email(
        self,
        message: GmailMessage,
    ):
        EmailMessage = Query()
        search_result = self.db.search(EmailMessage.id == message.id)

        # Hit old message, continue
        if search_result:
            self.logger.debug(f"Message {message.id} already processed")
            return

        # Hit new message without a notification
        trade = self.extract_order_detail(message.html)

        # Send notification
        sent = self.send_ntfy_notification(trade=trade)

        # If notification is sent successfully, add the ID to the database
        if sent:
            self.db.insert({"id": message.id})
            self.logger.debug(f"Notification sent for message {message.id}")

    def extract_order_detail(self, html_content: str):

        # Create a BeautifulSoup object
        soup = BeautifulSoup(html_content, "html.parser")

        # Use search string to find the parent element which contains all order details ("Bot:")
        element = soup.find(lambda tag: tag.string and "Bot:" in tag.string)
        container_element = element.parent.parent
        search_text = container_element.getText()

        # Check both patterns for a match
        match_opened = re.search(self.position_open_regex, search_text)
        match_closed = re.search(self.position_closed_regex, search_text)

        if match_opened:
            return OATradeOpened(
                bot=match_opened.group(1).strip(),
                symbol=match_opened.group(2).strip(),
                strategy=match_opened.group(3).strip(),
                position=match_opened.group(4).strip(),
                expiration=datetime.strptime(
                    match_opened.group(5).strip(), "%b %d, %Y"
                ),
                quantity=int(match_opened.group(6).strip()),
                cost=float(match_opened.group(7).replace("$", "").replace(",", "")),
                price=float(match_opened.group(8).strip()),
            )

        elif match_closed:
            return OATradeClosed(
                bot=match_closed.group(1).strip(),
                symbol=match_closed.group(2).strip(),
                strategy=match_closed.group(3).strip(),
                position=match_closed.group(4).strip(),
                expiration=datetime.strptime(
                    match_closed.group(5).strip(), "%b %d, %Y"
                ),
                quantity=int(match_closed.group(6).strip()),
                close_price=float(
                    match_closed.group(7).replace("$", "").replace(",", "")
                ),
                profit_loss=float(
                    match_closed.group(8).replace("$", "").replace(",", "")
                ),
            )
        else:
            raise ValueError("Unsupported email structure")
