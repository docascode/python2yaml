# -*- coding: UTF-8 -*-
import yaml
import re

summary = u' An object in the form "{activityId: *id of message to delete*,conversation: { id: *id of Slack\nchannel*}}".\n'
obj = {
    'value': summary
}

summary = "Recognizes the user's input.\n\n\n > [!NOTE]\n > When overridden in a derived\
    \ class, attempts to recognize the user\u2019s input.\n >"

summary = summary.replace('\u2019', "'")

exc = '<xref:botframework.connector.models.ErrorResponseException>'

exceptions = exc[6:-1]

PARAMETER_TYPE = "[(]((?:.|\n)*)[)]"
_first_part_ret_data = '** asdfasf (aaaaa or\n bbb) - dsc'
_type_pattern = re.compile(PARAMETER_TYPE, re.DOTALL)

exp = _type_pattern.findall(_first_part_ret_data)
print(exp)