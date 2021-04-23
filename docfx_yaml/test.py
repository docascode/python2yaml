# -*- coding: UTF-8 -*-
import yaml

summary = u' An object in the form "{activityId: *id of message to delete*,conversation: { id: *id of Slack\nchannel*}}".\n'
obj = {
    'value': summary
}

print(yaml.dump(obj, default_flow_style=False,
                indent=2, sort_keys=False))
