import re

PARAMETER_NAME = "[*][*](.*?)[*][*]"
PARAMETER_TYPE = "[[](.*?)[]]"
PARAMETER_DESCRIPTION = "[–][ ](.*)"

string = "**init_arg1** ([float](https://docs.python.org/3.6/library/functions.html#float)) – Parameter init_arg1 from class docstring.[aaa]\n"
arg_name = re.compile(ARG_NAME)
arg_type = re.compile(ARG_TYPE)
description = re.compile(ARG_DESCRIPTION)

print(re.findall(re.compile(ARG_NAME), string))
print(re.findall(arg_type, string))
print(re.findall(description, string))