import os

import requests

SLACK_AUTH_TOKEN = os.environ.get("SLACK_AUTH_TOKEN")


def schedule_hint_announcement(channel_id: str, utc_seconds: int) -> None:
    """
    Schedule a message announcing the release of a hint.
    :param channel_id: The slack channel ID.
    :param utc_seconds: Timestamp at which to make the announcement, in seconds since
    the epoch.
    """
    if SLACK_AUTH_TOKEN is None:
        return

    cancel_pending_announcements(channel_id)

    schedule_url = "https://slack.com/api/chat.scheduleMessage"
    headers = {"Authorization": "Bearer {}".format(SLACK_AUTH_TOKEN)}
    json = {
        "channel": channel_id,
        "post_at": utc_seconds,
        "text": "A hint is available!",
    }
    requests.post(schedule_url, json=json, headers=headers)


def cancel_pending_announcements(channel_id: str) -> None:
    """
    Cancel any announcements that we currently have pending to a slack channel.
    :param channel_id: The slack channel ID.
    """
    if SLACK_AUTH_TOKEN is None:
        return

    list_url = "https://slack.com/api/chat.scheduledMessages.list"
    cancel_url = "https://slack.com/api/chat.deleteScheduledMessage"
    headers = {"Authorization": "Bearer {}".format(SLACK_AUTH_TOKEN)}

    # Get all the messages that we have scheduled...
    r = requests.get(list_url, headers=headers)
    if r.status_code == 200:
        # ... for this channel ...
        messages = [
            message
            for message in r.json()["scheduled_messages"]
            if message["channel_id"] == channel_id
        ]

        # ... and cancel them.
        for message in messages:
            json = {"channel": channel_id, "scheduled_message_id": message["id"]}
            requests.post(cancel_url, json=json, headers=headers)
