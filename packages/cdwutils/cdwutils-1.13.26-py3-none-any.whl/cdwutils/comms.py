import slack


def send_slack_message(token, channel, text):
    """
    Send a message to slack channel
    """

    slack_client = slack.WebClient(token=token)
    return slack_client.chat_postMessage(channel=channel, text=text)
