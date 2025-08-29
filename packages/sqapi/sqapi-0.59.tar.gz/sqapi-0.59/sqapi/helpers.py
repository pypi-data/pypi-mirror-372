import argparse
import inspect
import os.path
import sys
import re

PARAM_OR_RETURNS_REGEX = re.compile(":(?:param|returns)")
RETURNS_REGEX = re.compile(":returns: (?P<doc>.*)", re.S)
PARAM_REGEX = re.compile(":param (?P<name>[\*\w]+): (?P<doc>.*?)"
                         "(?:(?=:param)|(?=:return)|(?=:raises)|\Z)", re.S)


def parse_docstring(docstring):
    """Parse the docstring into its components.
    :returns: a dictionary of form
              {
                  "short_description": ...,
                  "long_description": ...,
                  "params": {"name": "description", ...},
                  "returns": ...
              }
    """

    short_description = long_description = returns = ""
    params = {}

    if docstring:
        docstring = trim(docstring)

        lines = docstring.split("\n", 1)
        short_description = lines[0]

        if len(lines) > 1:
            long_description = lines[1].strip()

            params_returns_desc = None

            match = PARAM_OR_RETURNS_REGEX.search(long_description)
            if match:
                long_desc_end = match.start()
                params_returns_desc = long_description[long_desc_end:].strip()
                long_description = long_description[:long_desc_end].rstrip()

            if params_returns_desc:
                params = {
                    name: trim(doc)
                    for name, doc in PARAM_REGEX.findall(params_returns_desc)
                }

                match = RETURNS_REGEX.search(params_returns_desc)
                if match:
                    returns = reindent(match.group("doc"))

    return {
        "short_description": short_description,
        "long_description": long_description,
        "params": params,
        "returns": returns
    }


def trim(docstring):
    """trim function from PEP-257"""
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    # Current code/unittests expects a line return at
    # end of multiline docstrings
    # workaround expected behavior from unittests
    if "\n" in docstring:
        trimmed.append("")

    # Return a single string:
    return "\n".join(trimmed)


def reindent(string):
    return "\n".join(l.strip() for l in string.strip().split("\n"))


def create_parser(cls, parser=None):
    init = cls.__init__
    doc = inspect.getdoc(init)
    pparams = parse_docstring(doc)
    if parser is None:
        parser = argparse.ArgumentParser(
            #prog=os.path.basename(inspect.getfile(cls)),
            description="{short_description}\n{long_description}".format(**pparams),
            formatter_class=argparse.RawTextHelpFormatter, conflict_handler='resolve')
    sig = inspect.signature(init)
    for name, param in sig.parameters.items():
        if name in ('self'):
            continue
        if param.kind is not inspect.Parameter.POSITIONAL_OR_KEYWORD:
            continue

        desc = pparams.get("params").get(name, "").strip()
        default = param.default if param.default is not inspect.Parameter.empty else None
        type_ = param.annotation if param.annotation is not inspect.Parameter.empty else None

        if type_:
            helptxt = f"{desc}\ntype: {type_.__name__}  | default: {default}"
            action = "store_false" if type_.__name__ == 'bool' and default else ("store_true" if type_.__name__ == 'bool' else None)
            if action is not None:
                parser.add_argument(f"--{name}", default=default, dest=param.name, help=helptxt, action=action)
            else:
                parser.add_argument(f"--{name}", default=default, dest=param.name, type=type_, help=helptxt)
        else:
            helptxt = f"{desc}\ndefault: {default}"
            parser.add_argument(f"--{name}", default=default, dest=param.name, type=type_, help=helptxt)
        # helptxt = f"{desc}\ntype: {txttype}  | default: {default}"
        # print(action)
        # parser.add_argument(f"--{name}", default=default, dest=param.name, type=type_, help=helptxt, action=action)

    for base in cls.__bases__:
        parser = create_parser(base, parser=parser)
    return parser


def cli_init(cls, parser=None):
    params = create_parser(cls, parser=parser)
    args = params.parse_args()
    return cls(**vars(args))
