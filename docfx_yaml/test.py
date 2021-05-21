# -*- coding: UTF-8 -*-
import yaml

summary = u' An object in the form "{activityId: *id of message to delete*,conversation: { id: *id of Slack\nchannel*}}".\n'
obj = {
    'value': summary
}

summary = "Recognizes the user's input.\n\n\n > [!NOTE]\n > When overridden in a derived\
    \ class, attempts to recognize the user\u2019s input.\n >"

summary = summary.replace('\u2019', "'")

print(summary)
