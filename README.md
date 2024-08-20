# option-alpha-ntfy

# About

I recently restarted my journey with trading options after several years, with the [Option Alpha](https://optionalpha.com/) platform. They do not have a mobile app that supports push notifications, so I created a very simple application which takes the email alerts generated via the Option Alpha platform and turns them into notifications via the service [ntfy](https://ntfy.sh/), which is a free pub-sub notification service.

The only catch is that the free tier does not support "protected" topics, meaning anyone with the topic name can subscribe to your published data. While there isn't technically any sensitive data contained within these alerts, I felt more comfortable purchasing the lowest tier so that my trade data was on a private channel. The application supports both open and protected topics. They also support a self-hosted option, which I plan to support in the near future.

The alerts are just the markdown equivalent of the order details. The HTML is not exactly sematic so that was the most tedious part of writing this. The parsing logic is quite brittle but I imagine the structure will not change for some time. If any errors occur, please submit an issue.

# Requirements
- [Python 3.12](https://www.python.org/downloads/release/python-3125/)
- [pipenv](https://pipenv.pypa.io/en/latest/)

# Prerequisites

This application uses the package [simplegmail](https://github.com/jeremyephron/simplegmail) in order to retrieve emails from your Gmail inbox with a particular label. This dependency requires that you have a OAuth 2.0 Client ID file downloaded in this directory. The setup instructions can be found on the repository homepage. This requires that you have a Google Cloud account, which is somewhat tedious to setup from scratch if you are not already using the platform. In the future, I may stop using Gmail specific APIs and support any arbitrary email client. However, not having to manage a separate email account is a plus and the Option Alpha platform does not currently support adding secondary email addresses for notifications. Whichever address you used to open your account is the one that will be notified.

# Configuration Variables

| Name                    | Description                                                 | Default                                                                 |
|-------------------------|-------------------------------------------------------------|-------------------------------------------------------------------------|
| `gmail_label_id`         | The label ID for filtering Gmail messages                   | None                                                                   |
| `ntfy_topic_name`        | Topic name for the ntfy notifications                       | None                                                                   |
| `ntfy_protected_topic`   | Whether the ntfy topic is protected                         | `false`                                                                 |
| `ntfy_bearer_token`      | Bearer token for authenticating with ntfy                   | `null`                                                                  |
| `position_open_regex`    | Regular expression for parsing position open notifications  | `'Bot:\s*(.*?)Symbol:\s*(.*?)Strategy:\s*(.*?)Position:\s*(.*?)Expiration:\s*(.*?)Quantity:\s*(.*?)Cost:\s*(.*?)Price:\s*(.*)'` |
| `position_closed_regex`  | Regular expression for parsing position closed notifications| `'Bot:\s*(.*?)Symbol:\s*(.*?)Strategy:\s*(.*?)Position:\s*(.*?)Expiration:\s*(.*?)Quantity:\s*(.*?)Close Price\*:\s*(.*?)Profit/Loss:\s*(.*)'` |
| `sleep_time`             | Time interval between checks (in seconds)                   | `60`                                                                    |



# Setup
1. Create virtual environment and install requirements
    
    `pipenv install`

2. Spawn pipenv shell

    `pipenv shell`

3. Copy example config template.

    `cp config.example.ml config.yml`

4. Insert appropriate values where placeholders exist
    
    a. Find the appropriate Gmail label (run `python -m oa_ntfy --mode list_labels`) and copy the value to the `gmail_label_id` property

    b. Insert your desired ntfy topic name to the `ntfy_topic_name` property
    
    c. If using a protected topic, set the `ntfy_protected_topic` property to `true`

    d. If using a protected topic, set the `ntfy_bearer_token` property. Access tokens for ntfy can be found here: [Account Settings](https://ntfy.sh/account).


5. Run application

    `python -m oa_ntfy`
