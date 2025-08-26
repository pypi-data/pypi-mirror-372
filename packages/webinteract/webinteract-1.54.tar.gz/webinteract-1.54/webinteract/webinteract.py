#!/usr/bin/env python3

###############################################################################
#
# Copyright (c) 2022-2025, Anders Andersen, UiT The Arctic University
# of Norway. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# - Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################


R"""The `webinteract` module for simple web interaction

This module implements a simplified web interaction class. It is
implemented using the [`splinter`](https://splinter.readthedocs.io)
module (and `splinter` is implemented using the
[`selenium`](https://selenium-python.readthedocs.io) module).

The easiest way to install this module is to use `pip`:

```bash
pip install webinteract
```

This `pip` command will install the module and a console script
`webinteract` to use the module as a program. If you execute
`webinteract` without a web-interaction-action script (`wia` script)
as an argument, it will open a browser window and present you a prompt
in the terminal where you do your interaction with the web. For more
information, try either the `-h` argument to the console script
`webinteract` or type `help` in the prompt.

The web interaction approach of this module is to use simple web
interaction scripts where each line is a web interaction action.  The
web intedraction class `WebInteraction` implements all the different
action types, and it is meant to be easily extendible. This is an
example of a small web interaction actions script (stored in a file
`"add-ts.wia"`):

```python
#!/usr/bin/env webinteract
setvals(url="https://a.web.page/", account="an@email.address")
visit(url)
fill(account, "id", "loginForm:id")
fill(pw, "id", "loginForm:password")
click("id", "loginForm:loginButton")
verify( \
  is_text_present("Login succeeded", wait_time=19), True, \
  "The text 'Login succeeded' is not present")
fill(date, "id", "registerForm:timeStamp")
click("id", "registerForm:addTS")
verify( \
  is_text_present("Register time stamp failed"), False, \
  "The text 'Register time stamp failed' is present")
```

The first line is special kind of comment that will be discussed
later. The second line gives vaules to two variables, `url` and
`account`. If we look closer at the script, we see a few other
varibles also used in the script (`pw` and `date`). They have to be
added to the name space of the script with the `update` method or as a
command line argument before the script is executed.

To perform the small web interaction script above we can do this in
Python:

```python
# Import modules used in the example
from datetime import datetime
import webinteract			# This module

# Create a time stamp (an example variable used it the script)
ts = datetime.now().strftime("%Y%m%d-%H%M%S")

# Open browser
web = webinteract.WebInteraction()

# Add `pw` and `date` to the name space of the script
web.update(pw = "a s3cret p4ssw0rd", date = ts)

# Perform web interaction actions (the script)
web(open("add-ts.wia"))
```

Another approach is to execute the script directly. The first line of
web interaction actions script (`wia` script) is a comment with a
magic string telling the system what program to use to interpret the
script. In this example, the installed console script
`webinteract`. For this to work, the `wia` script file has to be
executable (`chmod +x add-ts.wia`). The only other thing we have to
remember is to provide values for the two unasigned variables in the
script.  We provide this with the `--name-space` argument (in JSON
format):

```bash
./add-ts.wia --name-space '{"pw": "a s3cret p4ssw0rd", "date": "20250102-030405"}'
```

In real usage, you should of course never include a password in plain
text. The `webinteract` module supports storage of passwords in a
keychain/keyring using the Python module `keyring`.

For more information, check out the following blog post:

 - https://blog.pg12.org/web-page-interaction-in-python

To print the help message with all the command line arguments for the
`webinteract` console script use the command line argument `--help`:

```bash
webinteract --help
```

To print this documentation and all available web actions use the
command line argument `--doc [ACTION]` (where the optional argument is
used to print the documentation of a specific web action):

```bash
webinteract --doc
```

"""


#
# Import some modules needed (other modules imported below in source
# code if needed)
#

# Need these
import sys, json
from functools import wraps
from pathlib import Path

# For the help command in interactive mode
from inspect import signature

# Used for the wait action
from time import sleep

# For type hints
from typing import Any, Literal, TypedDict, TextIO, Self
from collections.abc import Callable

# We use splinter to implement the web interaction
# https://splinter.readthedocs.io/
import splinter
from splinter.element_list import ElementList
from splinter.driver.webdriver import BaseWebDriver


#
# Help values/types
#


# Current version of module
version = "1.54"

# Nice to have a list of all web interaction actions
#_all_wia = [a[4:] for a in dir(WebInteraction) if a[:4] == '_mk_']

# Mapping to some functions from the spliter Driver API (and Browser API)
# https://splinter.readthedocs.io/en/stable/api/driver-and-element-api.html

# Web driver methods from splinter used in implementing (some) wia-actions
SplinterMethod = Callable[[BaseWebDriver, ...], Any]

# An wia-action can take any arguments and return anything
type ActionFunc = Callable[[...], Any]
type MakeActionFunc = Callable[[Self], ActionFunc]

# A stored wia-action is a dictionary with the wia-action, its name
# and its arguments (both in the *args and *kw form)
StoredAction = TypedDict(
    "StoredAction", {
        "action": ActionFunc, "name": str, "args": list, "kw": dict})

# A function wrapping the actual action returning the a StoredAction
type ActionWrapper = Callable[[...], StoredAction]

# The element action types used to locate elements (e.g., find_by_css, find_by_id, ...)
type ElementActionType = \
    Literal["find", "is_element_present", "is_element_not_present"]
_element_action_types: list[ElementActionType] = list(ElementActionType.__value__.__args__)

# Find element based on what?
type SelectorType = \
     Literal["css", "id", "name", "tag", "text", "value", "xpath"]
_selector_types: list[SelectorType] = list(SelectorType.__value__.__args__)

# Find links based on what?
type LinkActionType = \
    Literal["text", "partial_text", "href", "partial_href"]
_link_action_types: list[LinkActionType] = list(LinkActionType.__value__.__args__)

# The type of an API map to the Driver API (and Browser API) functions
EFuncMap = TypedDict("EFuncMap", {key: SplinterMethod for key in _selector_types})
LFuncMap = TypedDict("LFuncMap", {key: SplinterMethod for key in _link_action_types})
APIMap = TypedDict(
    "APIMap", {key: EFuncMap for key in _element_action_types} | {"link": LFuncMap})

# Information about wia-actions (and their make action functions)
ActionInfo = TypedDict("ActionInfo", {"mkf": MakeActionFunc, "sig": str, "mk_name": str})
ActionInfoMap = dict[str, ActionInfo]	# Where `str` is all wia

# Method (in WebInteraction) that processes each line of the input (`wia` script)
LineProcessor = Callable[[Self, str], None]

#
# Help functions
#


def _mk_api_map(the_browser: splinter.Browser) -> APIMap:
    R"""Create an API map to the Driver API (and Browser API) functions

    In the map (a dictionary), the functions can be accessed using an
    `_element_action_types` key and an `_selector_types` or `_link_action_types` key.
    Some examples of the content of the API map:

    ```
    api_map["find"]["id"] -> the_browser.find_by_id
    api_map["link"]["text"] -> the_browser.links.find_by_text
    ```

    Arguments/return value:

    `the_browser`: An instance of the Browser class with the functions
    (methods) to link to in the API map.

    `return`: The API map (a dictionary)

    """
    api_map: APIMap = {}
    for atype in _element_action_types:
        api_map[atype] = {}
        for stype in _selector_types:
            api_map[atype][stype] = \
                getattr(the_browser, atype + "_by_" + stype)
    api_map["link"] = {}
    for ltype in _link_action_types:
         api_map["link"][ltype] = \
             getattr(the_browser.links, "find_by_" + ltype)
    return api_map


# Some help functions for stored wia-actions


def _is_action(action: StoredAction, name: str = None) -> bool:
    R"""Is this an action (with a given name)

    Returns `True` if `action` is a stored wia-action. A stored
    wia-action is a dictionary including the keys `"action"`,
    `"name"`, `"args"`, and `"kw"`.  If the `name` argument is
    provided it has to match the name of the action.

    Arguments/return value:

    `action`: Verify that this is actually a stored wia-action

    `name`: If given, the action should match the name

    `return`: Returns `True` if `action` is a stored wia-action (and
    if name is provided, it matches the name of the action)

    """
    if type(action) is dict:
        if all(k in action for k in ("action", "name", "args", "kw")):
            if name and action["name"] == name:
                return True
            elif not name:
                return True
    return False


def _do_inline_action(action: StoredAction) -> str | bool | ElementList | None:
    R"""Execute the stored wia-action

    Perform the action stored in the dictionary with the store
    arguments.  `action["action"]` is the action (function) to call,
    and `action["args"]` and `action["kw"]` are the arguments.

    Arguments/return value:

    `action`: The stored wia-action (a dictionary including the actual
    function and its arguments)

    `return`: Whatever the action returns

    """
    return action["action"](*action["args"], **action["kw"])


def _prep_element(element: StoredAction | ElementList) -> str | bool | ElementList | None:
    R"""If element is stored action, perform it

    Prepare the element: if the the element is an Action perform the
    action and return the result, otherwise return the element.

    Arguments/return value:

    `element`: The element to prepare

    `returns`: An element

    """
    return _do_inline_action(element) if _is_action(element) else element


def _element_action_it(
        element: ElementList,
        index: int | None,
        action_str: str,
        *args: tuple,
        doall: bool = False,
        **kw: dict) -> str | bool | ElementList | None:
    R"""Perform an action on a web element

    Perform an action on a web element (`"fill"`, `"check"`, `"click"`
    and so on).

    Arguments/return value:

    `element`: A list of elements (result for a find operation). Often
    a list with a single element.

    `index`: Used to choose the actual element from the list of
    elements. Usually we choose the first element (index is 0).

    `action_str`: The name of the action performed (e.g, `"fill"`,
    `"check"`, `"click"`).

    `*args`: Positional arguments to the action performed.

    `doall`: If index is `None` and this is `True`, the action is
    performed on all matching web elements.

    `**kw`: Named arguments to the action performed.

    """
    failed = True	# Pesimistic
    if type(element) is ElementList:
        if index != None:
            elist = [element[index]]
        else:
            elist = element
        for e in elist:
            if hasattr(e, action_str):
                try:
                    action = getattr(e, action_str)
                    res = action(*args, **kw)
                    failed = False
                    if not doall:
                        return res
                except:
                    continue
    if failed:
        raise WebInteractionError(
            f"Web-element action failed: element[{index}].{action_str} " + \
            f"not found")

    
def _element_action(
        element: StoredAction | ElementList,
        index: int | None,
        action_str: str,
        *args: tuple,
        doall: bool = False,
        **kw: dict) -> str | bool | ElementList | None:
    R"""Find and perform an action on a web element

    Find the web-element using the provided `find_action` (a stored
    action) and then perform the action.

    Arguments/return value:

    `element`: A web element or a stored action used to find the web element.

    `index`: Used to choose the actual element from the list of
    elements. Usually we choose the first element (`index` is 0).

    `action_str`: The name of the action performed (e.g, `"fill"`,
    `"check"`, `"click"`).

    `*args`: Positional arguments to the action performed.

    `doall`: If index is `None` and this is `True`, the action is
    performed on all matching web elements.

    `**kw`: Named arguments to the action performed.

    """
    if _is_action(element):
        element = _do_inline_action(element)
    _element_action_it(element, index, action_str, *args, doall=doall, **kw)


#
# The web interact actions (wia) language implementation
#


def webaction(func: MakeActionFunc) -> ActionWrapper:
    R"""Web action decorator

    A decorator that wraps a web action. The wrapper stores the
    web-action in a dictionary structure and returns it. This stored
    web-action (dictionary) is later used to actually perform the call
    in a limited name space (using the `WebInteraction` class method
    `_do_action`).

    Arguments/return value:

    `func`: a function returning a web action. The name of the action
    is the name of the fuction except the four first characters
    (remove the `"_mk_"` part).

    `return`: A wrapper for the web action that returns a stored
    action.

    """

    # Grab the name (removing the "_mk_" part)
    name: str = func.__name__[4:]

    # The wrapper function
    @wraps(func) # Update the wrapper function to look like the wrapped func
    def wrapper(self, *args: tuple, **kw: dict) -> StoredAction:

        # Grab the action (returned by the `_mk_...` method)
        action: ActionFunc = func(self)

        # Store the action in a dictionary and return it
        return {
            "action": action,
            "name": name,
            "args": args,
            "kw": kw
        }

    # Replace the the make action method with the wrapper
    return wrapper


class WebPrompt:
    R"""Prompt for interactive web interaction

    Implementation of the interactive prompt for web interaction. The
    prompt is presented when the console script is called without a
    wia-script to execute.

    """

    def __init__(self, docs: dict[str: str], each_line: LineProcessor, args_dict: dict):
        R"""Initialize the interactive prompt

        Prepare the interactive prompt for web interaction actions,
        including help functions.

        Arguments:

        `docs`: The documentation of each web interaction action (the
        name of the action is the key).

        `each_line`: The method processing (the processor) each line in a wia-script.

        `args_dict`: Command line arguments.

        """

        # Save the documentation and the line processor
        self._docs = docs
        self._each_line = each_line

        # Colors: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
        # Supported, but not part of the Ansi standard: LIGHTBLACK_EX,
        # LIGHTRED_EX, LIGHTGREEN_EX, LIGHTYELLOW_EX, LIGHTBLUE_EX,
        # LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX
        from colorama import Fore
        if args_dict:
            prompt = "\033[1m" + args_dict["prompt"] + "\033[0m"
            prompt_color = eval("Fore." + args_dict["prompt_color"])
            output_color = eval("Fore." + args_dict["prompt_output_color"])
            alert_color = eval("Fore." + args_dict["prompt_alert_color"])
        else:
            prompt = "\033[1m" + "wia> " + "\033[0m"
            prompt_color = Fore.CYAN
            output_color = Fore.GREEN
            alert_color = Fore.RED
        self.message = prompt_color + prompt + Fore.RESET
        self.output = output_color + "%(msg)s" + Fore.RESET
        self.alertit = alert_color + "%(msg)s" + Fore.RESET
        
        # Use `prompt_toolkit`
        from prompt_toolkit import PromptSession, print_formatted_text, ANSI
        from prompt_toolkit.history import FileHistory
        self.printit = lambda m, *a, **k: print_formatted_text(ANSI(m), *a, **k)
        self.session = PromptSession(
            message = ANSI(self.message),
            history = FileHistory(Path.home() / ".wia_history"))
        
        # Map to the shell specific commands
        self.shell_cmd = {
            #"history": self.history, "hdrop": self.hdrop,
            #"hclear": self.hclear,
            "help": self.help, "doc": self.doc, "exit": self.exit}

        # Add prompt command help (documentation)
        self.prompt_cmd_help = ""
        for cmd in self.shell_cmd.keys():
            self.prompt_cmd_help += "\n" + cmd + ": " + \
                self.shell_cmd[cmd].__doc__

        # Add action specific help functions
        for adoc in self._docs:
            self.shell_cmd["help " + adoc] = self.help

    # Some shell (prompt) specific commands:

    def help(self, line: str):
        R"""Print help text

        Print help text for a specific action or the generic help text.

        Arguments:

        `line`: The help command.

        """
        if line[5:] in self._docs:
            self.out(self._docs[line[5:]])
        else:
            actions = _list_actions(self._docs)
            self.out(
                "Available web actions:\n" + \
                "======================\n" + \
                actions + "\n" + \
                "-------------------------------\n" + \
                "Use 'help <action>' for details\n" + \
                "-------------------------------\n" + \
                "The prompt commands:" + \
                self.prompt_cmd_help)

    # The module doc string
    def doc(self, line: str):
        R"""Print module documentation

        The module documentation (from the `__doc__` attribute) is presented.
        
        Arguments:

        `line`: Ignored.
        
        """
        self.out(__doc__.strip() + "\n")

    # Exit prompt
    def exit(self, line: str):
        R"""Exit interactive prompt

        A command used the exit the interactive prompt. The exit
        happens at the callee. The method just informas that it wants
        to exit.

        Arguments/Return value:

        `line`: Ignored.

        `return`: The text "exit".

        """
        return "exit"

    # The interactive prompt and processing

    def _msg(self, msg: str, what: str, *args: tuple, **kw: dict):
        R"""Generic message

        Present a message to the interactive user.
        
        Arguments:

        `msg`: The message to present.

        `what`: The type/format of the message.

        `args`: Other arguments (to `printit`)

        `kw`: Other keyword arguments (to `printit`)

        """
        self.printit(what % {"msg": msg}, *args, **kw)

    def out(self, msg: str):
        R"""Normal output message

        Present an output message to the interactive user.
        
        Arguments:

        `msg`: The message to present.

        """
        self._msg(msg, self.output)

    def alert(self, msg: str):
        R"""Alert message

        Present an alert message to the interactive user.

        Arguments:

        `msg`: The message to present.

        """
        self._msg(msg, self.alertit, flush=True)
    
    # Present prompt and get input
    def get_input(self) -> str:
        R"""Present prompt and get input

        Present the prompt, fetch the input, and return it

        Return value:

        `return`: The input (a line).

        """
        return self.session.prompt()
        
    def process_input(self, line: str):
        R"""Process the input

        Internal shell (prompt) commands (help, exit, ...) are handled
        here and web interaction actions are processed by the line
        processor.

        Arguments:

        `line`: The line to process

        """
        stripped_line: str = line.strip()
        if stripped_line in self.shell_cmd:
            self.shell_cmd[stripped_line](stripped_line)
        elif stripped_line[:5] == "help ":
            self.alert(f"Help: unknown action '{stripped_line[5:]}'\n")
        elif stripped_line == "":
            pass
        else:
            try:
                result = self._each_line(line)
                if result != None:
                    self.out(repr(result))
                    return result
            except Exception as err:
                self.alert(
                    f"Web page interaction failed: '{line}'\n" + \
                    f"Error: {err}\n")


class WebInteractionError(Exception):
    R"""Web interaction error

    An error raised when a web interaction action (web action) fails.

    """
    pass


class WebInteraction:
    R"""The web interaction class for web sessions

    The web interaction class `WebInteraction` creates web interaction
    objects that can interpret a series of web interaction actions
    (web-actions).  When an instance of the class is created, a web
    session, with a companion web browser where the web actions are
    performed, is also created. The class implements all the web
    actions and, in addition, the following methods for preparing,
    performing, and terminating the web interaction session:

     - `update`: Update the namespace for the web actions

     - `execute`: Perform the web actions from a `wia` script or
       interactivly (presenting a web interaction prompt).  This
       method is also called when an instance of the `WebInteraction`
       class is called as a function, and it is the main function of
       the `WebInteraction` class.

     - `quit`: Exit the web interaction session (and the web browser
       created when `WebInteraction` was instanciated).

    """

    def __init__(self, *args: tuple, **kw: dict):
        R"""Instanciate a web interaction object

        When a web interaction object is created, a web session is
        started and all the preparations to perform web actions are
        done. This includes creating the initial namespace for the web
        actions and creating the web browser where the actions are
        performed.
        
        The arguments are equal to the arguments used to instanciate a
        `Browser` object from the `splinter` module.  For details, see the
        documentation at

         - https://splinter.readthedocs.io/

        If the default behavior of the `Browser` class from `splinter`
        is OK, no arguments are necessary.

        Arguments:

        `*args`: positional arguments to the the `Browser` constructor

        `**kw`: named arguments to the the `Browser` constructor

        """

        # The browser used to interact with the web pages
        self._browser: splinter.Browser = splinter.Browser(*args, **kw)
        self._api_map: APIMap = _mk_api_map(self._browser)

        # Default no prompt
        self.prompt = None


        # The available functions in the name space of the web actions:
        # Find all methods starting with _mk_ and add them to namespace
        self._ns: dict[str, Any] = {}
        for k in dir(self):
            if k[:4] == "_mk_":	
                self._ns[k[4:]] = getattr(self, k)
        
        # The name space can be populated with other names, but the
        # ones initialized here are read-only (safe keys) and should
        # never be updated
        self._safekeys: list = list(self._ns.keys())

        # Module and action documentation
        self._docs = _make_docs()

        # Current action (code string) and line number (in a wia-script)
        self._current_action: str | None = None
        self._lineno: int = 0

        # To handle multiline commands (lines ending with '\')
        self._multi: str = ""

    def _do_action(self, action_code: str) -> str | bool | ElementList | None:
        R"""Perform a web interaction action

        Perform the saved web interaction action, and if specified,
        check the reurn value of the action.

        Arguments/return value:

        `action`: The action (a line in the web interaction action script)

        `return`: Whatever the action returns

        """

        # Save current action (string)
        self._current_action = action_code

        # Create stored action
        try:
            action: StoredAction = eval(
                action_code, {"__builtins__": None}, self._ns)
        except Exception as err:
            msg = f"Create action failed: {action_code} \n"
            msg += f"{str(err)}"
            raise WebInteractionError(msg)
            
        # Perform the action and save the return value (the result)
        try:
            result = action["action"](*action["args"], **action["kw"])
        except Exception as err:
            msg = f"Perform action failed: {action_code} \n"
            msg += f"{str(err)}"
            raise WebInteractionError(msg)

        # Drop current action
        self._current_action = None

        # Return result (might be None and/or ignored)
        return result

    def _each_line(self, line: str) -> str | bool | ElementList | None:
        R"""Process a line of a script (or from the prompt)

        Process a line of a script and also handle multi line action
        (a line ending with a back-slash).

        Arguments/return value:

        `line`: A line in the web interaction action script

        `return`: Whatever the action returns

        """
        
        # Count current line and remove any spaces before and after
        self._lineno += 1
        stripped_line: str = line.strip()

        # Ignore comments line
        if stripped_line and stripped_line[0] == "#":
            return

        # A multi-line action is merged to a single line
        if stripped_line and stripped_line[-1] == "\\":
            self._multi += stripped_line[:-1]
            return
        else:
            stripped_line = self._multi + stripped_line
            self._multi = ""

        # Perform the action if it is not empty
        if stripped_line:
            return self._do_action(stripped_line)

    def __call__(self, *args, **kw):
        R"""If an instance is called as a function, perform the `execute` method"""
        self.execute(*args, **kw)

    def execute(self, file: TextIO | None = None,
                args_dict: dict | None = None):
        R"""Read and and execute the web interaction action script

        This perform the actual execution of the web interaction
        action script using the web interaction action language
        defined by the functions in the web interaction action name
        space.

        This method is called when an instance of the `WebInteraction`
        class is called like a function.

        Arguments:

        `file`: The file object with the web interaction action script
        (any object implementing Python text i/o will do:
        https://docs.python.org/3/library/io.html). If this is `None`,
        read web interaction actions from a prompt.

        """

        # Read web interaction actions from the wia script file
        if file or not sys.stdout.isatty():

            # Read from stdin
            if not file:
                file = sys.stdin
        
            # Read and execute each line of the script
            for line in file:
                result = self._each_line(line)
                if result != None:
                    print(result, file=args_dict["output_file"])
                
        # If no file, read web interaction actions from a prompt   
        else:

            # Prepare web prompt
            self.prompt = WebPrompt(self._docs, self._each_line, args_dict)

            # Get input until exit
            while (line := self.prompt.get_input()) != 'exit':
                result = self.prompt.process_input(line)
                if 'exit' in line and result == 'exit':
                    break
                elif result != None:
                    print(result, file=args_dict["output_file"])

        # Hmm, a left over action (non terminated multi line)
        if self._multi and self._multi[0] != "#":
            self._do_action(self._multi)
            
    def update(self, *args: tuple[dict[str, Any]], **kw: dict[str, Any]):
        R"""Update the namespace

        Update the web interaction action namespace with variables
        that can be used in the scripts (typically values used as
        arguments to the fuctions that can not be specified directly
        in the scripts). If `web` is a `WebInteraction` instance,
        these two `update` calls perform the same update:

        ```python
        web.update({"pw": "a s3cret p4ssw0rd", "date": ts})
        web.update(pw = "a s3cret p4ssw0rd", date = ts)
        ```

        Arguments:

        `*args`: positional arguments, name space (dictionary)
        mapping names to values.

        `**kw`: named arguments, mapping names to values

        """

        # Get the update namespace from the arguments
        ns = {}
        if args:
            for n in args:
                ns.update(n)
        if kw:
            ns.update(kw)

        # Is the keys in the updated name space valid?
        for key in ns.keys():
            if key in self._safekeys:
                raise PermissionError(
                    f"Can not update read-only '{key}' in name space")

        # Update the name space
        self._ns.update(ns)

    def quit(self):
        R"""Quit the browser

        Quit the browser and terminate the web interaction session.

        """
        self._browser.quit()

    def __setitem__(self, key: str, val: Any):
        R"""Add variable to name space

        Add a variable to the name space of the web interaction actions.

        Arguments/return value:

        `key`: the name of the variable

        `val`: the value of the variable
        
        """

        # Only change non safe (non read-only) variables
        if not key in self._safekeys:

            # Add or update variable with name `key` and value `val`
            self._ns[key] = val
            
        else:

            # Raise error of we try to update safe variable
            raise PermissionError(
                f"Can not update read-only '{key}' in name space")

    def __getitem__(self, key: str) -> Any:
        R"""Get variable from name space

        Return the value of a variable in the name space of the web
        interaction actions.

        Arguments/return value:

        `key`: the name of the variable to return the value of

        """

        # Safe keys are not returned (they are internal)
        if not key in self._safekeys:
            return self._ns[key]
        else:
            raise KeyError(f"{key}")

    def _do_find(
            self,
            stype: SelectorType, sval: str,
            element: ElementList = None, index: int = 0) -> ElementList:
        R"""Do different find actions

        Returns a list of elements matching the selector `stype` with
        the value `sval` (often containing a single element). If the
        `element` argument is given, find web elments conatined in the
        given element.

        Arguments/return value:

        `stype`: An SelectorType, meaning one of the following:
        `"css"`, `"id"`, `"name"`, `"tag"`, `"text"`, `"value"`, or
        `"xpath"`.

        `sval`: The value to match (e.g., the id of an element).

        `element`: A list of the web elements (default None -> find global).

        `index`: Choose from the list of elements (default 0).

        `return`: A list of matching elments (often, just a list of one).

        """
        if element:
            find_by_ = getattr(element[index], "find_by_" + stype)
            return find_by_(sval)
        elif stype in self._api_map["find"] and sval:
            return self._api_map["find"][stype](sval)
        else:
            raise WebInteractionError(
                f"find: Unknown type or missing value ({stype}: {sval})")

    def current_action_info(self) -> str:
        if self._current_action:
            return f'{self._lineno}: "{self._current_action}"'
        else:
            return ""

    # All the remaining method names starts with "_mk_" and they are
    # the predefined web interaction actions. Some functions are
    # implemented inside the method and some are mapping to the
    # coresponding `splinter` browser object. The name is created from
    # the method name (removing the "_mk_" part). The work is done in
    # the `webaction` decorater. The method should return a fuction
    # implementing the web interaction action.  Add new methods below
    # with the `webaction` decorator to extend the web interaction
    # action language (the wia language).

    @webaction
    def _mk_wait(self) -> ActionFunc:
        R"""Action `wait` waits for the given seconds in a script

        Used if you need to wait for web elements to be loaded or when
        debugging scripts. Some other actions, like `is_present`, can
        also wait for a while if the expected element is not present
        yet (they have an optional argument `wait_time`).

        Arguments:

        `wait_time`: The amount of time to wait in seconds (default 1).

        """

        # The implementation of the action
        def wait(wait_time: int = 1):
            sleep(wait_time)
        
        # Return the action
        return wait

    @webaction
    def _mk_dialog(self) -> ActionFunc:
        R"""Action `dialog` set values from user input

        The `dialog` action is a way for a `wia` script to get input
        from the user (or block the execution of the script until the
        user gives some input).  This example provides a short
        description and set the values of `user` and `age` in the name
        space:

        ```python
        dialog("Please set user and age:", user="User", age="Age")
        ```

        This example present a short description and blocks the script
        until the user press return (no values are set):

        ```python
        dialog("Check the filled in form and press return to submit")
        ```

        Arguments:

        `dialog_text`: A description of the expected input (default "",
        meaning the description is not presented).

        `kw`: Named arguments that describes values in the namespace
        for each input from the user.

        """

        # The implementation of the action
        def dialog(dialog_text: str = "", **kw):

            # Print decriptive text if given
            if dialog_text:
                printit(dialog_text + "\n")

            # Set value to each variable in namespace from user input
            if kw:
                ns = {}
                for n in kw:
                    printit(kw[n] + ": ")
                    ns[n] = input()
                self.update(ns)

            # No variables? Continue wia script when user press return
            # (typically used when user have to type input at a web page)
            else:
                printit("Press return to continue ")
                input()

        # Create the output function
        if self == None:
            printit = lambda t: None	# The case when the signature of the action is grabbed
        elif self.prompt:
            printit = lambda t: self.prompt._msg(t, self.prompt.output, end="")
        else:
            printit = lambda t: print(t, end="")

        # Return the action
        return dialog                

    @webaction
    def _mk_setvals(self) -> ActionFunc:
        R"""Action `setvals` sets values used later in the script

        The `setvals` action can be used to give a value to one or more
        variables used later in the script.  This example sets the
        values of the two variables `url` and `email`:

        ```python
        setvals(url = "https://a.web.page/", email = "an@email.address")
        ```

        The variables `url` and `email` can then be used in other
        actions later in the script. `setvals` updates the name space
        of the script with the varibales with the given value.

        It is also possible to use web actions that returns a value
        with `setvals`. In this example we set the value of the
        variable `tag` to the value of an element with an id `"tag"`:

        ```python
        setvals(tag = get_value("id", "tag"))
        ```

        Arguments/return:

        `**kw`: Named arguments that set values in the namespace.

        """

        # The implementation of the action
        def setvals(**kw):

            # If the value is an action call, perform the action
            for k in kw:
                va = kw[k]
                kw[k] = _prep_element(va)
            
            # Update the namespace
            self.update(kw)

        # Return the action
        return setvals

    @webaction
    def _mk_verify(self) -> ActionFunc:
        R"""Action `verify` checks that two values match

        The created action checks that the two given value arguments
        match.  If they don't match and the `assert_it` argument is
        `True` (the default), the `WebInteractionError` is raised (the
        wia-script terminates). If they don't match and the
        `assert_it` argument is `False`, the action returns
        `False`. Each value argument is either a value or an
        action. If it is an action, the action is performed and the
        result of the action is the value compared with the other
        argument. Three examples:

        ```python
        verify(url, "https://a.web.page/")
        verify(is_present("id", "afilter"), True, "No filter")
        verify("web", get("id", "searchtxt"), "Action fill failed")
        ```

        The first example verifies that `url` has the value
        `"https://a.web.page/"`. The second example verifies that a web
        element with id `"afilter"` is present (`is_element_present`
        returns `True`). The third example verifies that a web element
        with id `"searchtxt"` has the value (or text) `"web"` (`get`
        returns `"web"`).

        The third optional argument is the error message given if the
        verification fails and the `WebInteractionError` is
        raised.

        Arguments/return value:

        `val1`: Value one.

        `val2`: Value two.

        `errmsg`: The error message given if the verification fails
        and the `WebInteractionError` is raised.

        `assert_it`: Should the action raise the `WebInteractionError`
        if the values don't match. The default is `True`.

        `return`: `True` if the two values match, `False`
        otherwise. If the `assert_it` argument is `True`, the
        WebInteractionError exception is raised if the two values do
        not match, and if they match, nothing is returned (and nothing
        happens).

        """

        # The implementation of the action
        def verify(
                val1: Any, val2: Any,
                errmsg: str = "No match",
                assert_it: bool = True) -> bool | None:
            v1 = _prep_element(val1)
            v2 = _prep_element(val2)
            if v1 != v2:
                if assert_it:
                    raise WebInteractionError(
                        f'Action "verify": failed: "{errmsg}" ({v1} != {v2})\n')
                else:
                    return False
            if not assert_it:
                return True

        # Return the action
        return verify
    
    @webaction
    def _mk_visit(self) -> ActionFunc:
        R"""Action `visit` is used to open a web page (URL)

        This action opens a web page (URL). The actions that follow
        will interact with this web page:

        ```python
        visit("https://a.web.page/")
        ```

        Actions following this action operates on this web page. The
        arguments to this action is the same as the `visit` method
        from the `Browser` class in the `splinter` module
        (https://splinter.readthedocs.io/en/latest/browser.html). To
        be more presise, the returned method is the `visit` method
        from the `Browser` class in the `splinter` module (and for moe
        detailed documentation, please use the `splinter` module
        documentation).

        Arguments/return value:

        `url`: The URL to be visited.

        """

        # The implementation of the action
        def visit(url: str):
            self._browser.visit(url)
        
        # Return the action
        return visit
    
    @webaction
    def _mk_find(self) -> ActionFunc:
        R"""Action `find` finds web elements on a web page

        This action finds web elements based on a selector type and
        the value of such a selector. This example returns a list of
        web elements with the id `"filter"` (often a list with a single
        element):

        ```python
        find("id", "filter")
        ```

        Another example using an XPath selector to find all `a`
        (anchor) elements with an attribute `title` that has the value
        `"log out"` (often a list with a single element):

        ```python
        find("xpath", "//a[@title='log out']")
        ```

        Arguments/return value:

        `stype`: The selector type (either `"css"`, `"id"`, `"name"`,
        `"tag"`, `"text"`, `"value"`, or `"xpath"`).

        `sval`: The value of the selector type.

        `return`: A list of the web elements matching the selector
        `stype` with the value `sval`.

        """

        # The implementation of the action
        def find(stype: SelectorType, sval: str) -> ElementList:
            return self._do_find(stype, sval)

        # Return the action
        return find
    
    @webaction
    def _mk_find_in_element(self) -> ActionFunc:
        R"""Action `find_in_element` finds web elements inside the web element

        This action finds web elements based on a selector type and
        the value of such a selector inside the given web
        element. This example returns a list of web elements with the
        name `"filter"` from inside a web element with the id
        `"form"`:

        ```python
        find_in_element("name", "filter", find("id", "form"), 0)
        ```

        Arguments/return value:
        
        `stype`: The selector type (either `"css"`, `"id"`, `"name"`,
        `"tag"`, `"text"`, `"value"`, or `"xpath"`).

        `sval`: The value of the selector type.

        `element`: Find the web element inside one of these elements.

        `index`: Choose from the list of elements (default 0).        

        `return`: A list of the web elements matching the selector
        `stype` with the value `sval`.

        """

        # The implementation of the action
        def find_in_element(
                stype: SelectorType, sval: str,
                element: ElementList, index: int = 0) -> ElementList:
            element = _prep_element(element)
            return self._do_find(stype, sval, element, index)

        # Return the action
        return find_in_element
    
    @webaction
    def _mk_element_get(self) -> ActionFunc:
        R"""Action `element_get` gets the value or text of the web element

        Get the value or text of the given web element.

        Arguments/return value:

        `element`: A list of the web elements.

        `index`: Choose from the list of matching elements (default 0).

        `return`: The value or text of a web element.

        """

        # The implementation of the action
        def element_get(element: ElementList, index: int = 0) -> str:
            element = _prep_element(element)[index]
            return element.value if element.value else element.text

        # Return the action
        return element_get
    
    @webaction
    def _mk_get(self) -> ActionFunc:
        R"""Action `get` gets the value or text of a web element

        Get the value or text of a web element matching the selector
        `stype` with the value `sval`. An example where we get the
        value or text of an element with the id `"about"`:

        ```python
        get("id", "about")
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default 0).

        `return`: The value or text of a web element matching the
        selector `stype` with the value `sval`.

        """

        # The implementation of the action
        def get(stype: SelectorType, sval: str, index: int = 0) -> str:
            element = self._do_find(stype, sval)[index]
            return element.value if element.value else element.text

        # Return the action
        return get
    
    @webaction
    def _mk_element_get_value(self) -> ActionFunc:
        R"""Action `element_get_value` gets the value of the web element

        Get the value of the web element.
        
        Arguments/return value:

        `element`: A list of the web elements.

        `index`: Choose from the list of elements (default 0).
        
        `return`: The value of the web element.

        """

        # The implementation of the action
        def element_get_value(element: ElementList, index: int = 0) -> str:
            return _prep_element(element)[index].value

        # Return the action
        return element_get_value
    
    @webaction
    def _mk_get_value(self) -> ActionFunc:
        R"""Create action `get_value` gets the value of a web element

        Get the value of a web element matching the selector stype
        with the value sval. An example where we get the value of an
        element with the name `"aggregate"`:

        ```python
        get_value("name", "aggregate")
        ```
        
        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default 0).
        
        `return`: The value of a web elements matching the selector
        `stype` with the value `sval`.

        """

        # The implementation of the action
        def get_value(stype: SelectorType, sval: str, index: int = 0) -> str:
            element = self._do_find(stype, sval)[index]
            return element.value 

        # Return the action
        return get_value
    
    @webaction
    def _mk_element_is_checked(self) -> ActionFunc:
        R"""Action `element_is_checked` checks if the web element is checked

        Check if the web element (checkbox) is checked.
        
        Arguments/return value:

        `element`: A list of the web elements.

        `index`: Choose from the list of elements (default 0).
        
        `return`: True if the web element (checkbox) is checked.

        """

        # The implementation of the action
        def element_is_checked(element: ElementList, index: int = 0) -> bool:
            return _prep_element(element)[index].checked

        # Return the action
        return element_is_checked
    
    @webaction
    def _mk_is_checked(self) -> ActionFunc:
        R"""Create action `is_checked` checks if a web element is checked

        Returns true if a web element matching the selector stype with
        the value sval is checked. An example where we check
        an element with the name `"checkbox1"`:

        ```python
        is_checked("name", "checkbox1")
        ```
        
        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default 0).
        
        `return`: True if a web element (checkbox) matching the
        selector `stype` with the value `sval` is checked.

        """

        # The implementation of the action
        def is_checked(stype: SelectorType, sval: str, index: int = 0) -> str:
            element = self._do_find(stype, sval)[index]
            return element.checked 

        # Return the action
        return is_checked
    
    @webaction
    def _mk_element_get_text(self) -> ActionFunc:
        R"""Action `element_get_text` gets the text of the web element
        
        Returns true if te web element is checked.

        Arguments/return value:

        `element`:  A list of the web elements.

        `index`: Choose from the list of elements (default 0).
        
        `return`: The text of the web element.

        """

        # The implementation of the action
        def element_get_text(element: ElementList, index: int = 0) -> str:
            return _prep_element(element)[index].text

        # Return the action
        return element_get_text
    
    @webaction
    def _mk_get_text(self) -> ActionFunc:
        R"""Action `get_text` gets the text of a web element

        Get the text of a web element matching the selector stype with
        the value sval. An example where we get the text of the third
        element (at index 2) with the tag `"h2"`:

        ```python
        get_text("tag", "h2", 2)
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default 0).
        
        `return`: The text of a web elements matching the selector
        `stype` with the value `sval`.

        """

        # The implementation of the action
        def get_text(stype: SelectorType, sval: str, index: int = 0) -> str:
            element = self._do_find(stype, sval)[index]
            return element.text

        # Return the action
        return get_text
    
    @webaction
    def _mk_element_check(self) -> ActionFunc:
        R"""Action `element_check` checks the web element (checkbox)

        Check the checkbox web element.
        
        Arguments/return value:

        `element`:  A list of the web elements.

        `index`: Choose from the list of elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def element_check(element: ElementList, index: int | None = None,
                          doall: bool = False):
            _element_action(element, index, "check", doall=doall)

        # Return the action
        return element_check

    @webaction
    def _mk_check(self) -> ActionFunc:
        R"""Action `check` checks a web element (checkbox)

        Check a checkbox web element matching the selector `stype`
        with the value `sval`. This example checks the fourth checkbox
        on the web page (with index 3):

        ```python
        check("xpath", "//input[@type='checkbox']", 3)
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def check(stype: SelectorType, sval: str, index: int | None = None,
                  doall: bool = False):
            element = self._do_find(stype, sval)
            _element_action_it(element, index, "check", doall=doall)

        # Return the action
        return check
    
    @webaction
    def _mk_element_uncheck(self) -> ActionFunc:
        R"""Action `element_uncheck` unchecks the web element (checkbox)

        Uncheck the checkbox web element.

        Arguments/return value:

        `element`:  A list of the web elements.

        `index`: Choose from the list of elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def element_uncheck(element: ElementList, index: int | None = None,
                            doall: bool = False):
            _element_action(element, index, "uncheck", doall=doall)

        # Return the action
        return element_uncheck
    
    @webaction
    def _mk_uncheck(self) -> ActionFunc:
        R"""Action `uncheck` unchecks a web element (checkbox)

        Uncheck a checkbox web element matching the selector `stype`
        with the value `sval`. This example unchecks a checkbox with
        id `"include-comments"`:

        ```python
        uncheck("id", "include-comments")
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def uncheck(stype: SelectorType, sval: str, index: int | None = None,
                    doall: bool = False):
            element = self._do_find(stype, sval)
            _element_action_it(element, index, "uncheck", doall=doall)

        # Return the action
        return uncheck
    
    @webaction
    def _mk_element_clear(self) -> ActionFunc:
        R"""Action `element_clear` clears the web element

        Reset the field value of the web element.

        Arguments/return value:

        `element`:  A list of the web elements.

        `index`: Choose from the list of elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def element_clear(element: ElementList, index: int | None = None,
                          doall: bool = False):
            _element_action(element, index, "clear", doall=doall)

        # Return the action
        return element_clear
    
    @webaction
    def _mk_clear(self) -> ActionFunc:
        R"""Action `clear` clears a web element

        Reset the field value of a web element matching the selector
        `stype` with the value `sval`. This example clears a field
        with the name `"search"`:

        ```python
        clear("name", "search")
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def clear(stype: SelectorType, sval: str, index: int | None = None,
                  doall: bool = False):
            element = self._do_find(stype, sval)
            _element_action_it(element, index, "clear", doall=doall)

        # Return the action
        return clear
   
    @webaction
    def _mk_element_click(self) -> ActionFunc:
        R"""Action `element_click` clicks the web element (button)

        Click on the web element.
        
        Arguments/return value:

        `element`: A list of the web elements.

        `index`: Choose from the list of elements (default `None`).

        """

        # The implementation of the action
        def element_click(element: ElementList, index: int | None = None):
            _element_action(element, index, "click")

        # Return the action
        return element_click
    
    @webaction
    def _mk_click(self) -> ActionFunc:
        R"""Action `click` clicks a web element (button)

        Click on a web element matching the selector `stype` with the
        value `sval`. This example clicks on a web element with the
        text `"OK"` (typically a button):

        ```python
        click("text", "OK")
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default `None`).

        """

        # The implementation of the action
        def click(stype: SelectorType, sval: str, index: int | None = None):
            element = self._do_find(stype, sval)
            _element_action_it(element, index, "click")

        # Return the action
        return click    

    @webaction
    def _mk_element_select(self) -> ActionFunc:
        R"""Action `element_select` selects the value in the web element

        Select the given value `val` in the select web the element.

        Arguments/return value:

        `val`: The value to fill in.

        `element`: A list of the web elements.

        `index`: Choose from the list of elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def element_select(val: str, element: ElementList,
                           index: int | None = None, doall: bool = False):
            _element_action(element, index, "select", val, doall=doall)

        # Return the action
        return element_select
    
    @webaction
    def _mk_select(self) -> ActionFunc:
        R"""Action `select` selects the value in a web element

        Select the given value `val` in a select web element matching
        the selector `stype` with the value `sval`. In this example,
        `"year"` is selected in the web element with the name
        `"type"`:

        ```python
        select("year", "name", "type")
        ```

        Arguments/return value:

        `val`: The value to fill in.

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def select(val: str, stype: SelectorType, sval: str,
                   index: int | None= None, doall: bool = False):
            element = self._do_find(stype, sval)
            _element_action_it(element, index, "select", val, doall=doall)

        # Return the action
        return select
    
    @webaction
    def _mk_element_fill(self) -> ActionFunc:
        R"""Action `element_fill` fills the value in the element

        Fill in the value `val` in the web element.
        
        Arguments/return value:

        `val`: The value to fill-in.

        `element`: A list of the web elements.

        `index`: Choose from the list of elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def element_fill(val: str, element: ElementList,
                         index: int | None = None, doall: bool = False):
            _element_action(element, index, "fill", val, doall=doall)

        # Return the action
        return element_fill
    
    @webaction
    def _mk_fill(self) -> ActionFunc:
        R"""Action `fill` fills the value in a web element

        Fill in the value `val` in a web element matching the selector
        `stype` with the value `sval`. In this example, a web element with
        the name `"search"` is filled with the text `"Python"`:

        ```python
        fill("Python", "name", "search")
        ```
        
        Arguments/return value:

        `val`: The value to fill-in.

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default `None`).

        `doall`: If index is `None` and this is `True`, the action is
        performed on all matching web elements.

        """

        # The implementation of the action
        def fill(val: str, stype: SelectorType, sval: str,
                 index: int | None = None, doall: bool = False):
            element = self._do_find(stype, sval)
            _element_action_it(element, index, "fill", val, doall=doall)

        # Return the action
        return fill

    @webaction
    def _mk_element_scroll_to(self) -> ActionFunc:
        R"""Action `element_scroll_to` scrolls to the web element

        Scroll to the web element.
        
        Arguments/return value:

        `element`: A list of the web elements.

        `index`: Choose from the list of elements (default `None`).

        """

        # The implementation of the action
        def element_scroll_to(element: ElementList, index: int | None = None):
            _element_action(element, index, "scroll_to")

        # Return the action
        return element_scroll_to
    
    @webaction
    def _mk_scroll_to(self) -> ActionFunc:
        R"""Action `scroll_to` scrolls to a web element

        Scroll to a web element matching the selector `stype` with the
        value `sval`. In this example, the view is scrolled to a `div`
        element with a `class` attribute having the value
        `"signature"`:

        ```python
        scroll_to("xpath", "//div[@class='signature']")
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default `None`).

        """

        # The implementation of the action
        def scroll_to(stype: SelectorType, sval: str, index: int | None = None):
            element = self._do_find(stype, sval)
            _element_action_it(element, index, "scroll_to")

        # Return the action
        return scroll_to

    @webaction
    def _mk_find_link(self) -> ActionFunc:
        R"""Action `find_link` finds link elements

        The action `find_link` returns link web elements based on a
        link selector type and the value of such a link selector. This
        example returns a list of link elements with `href` attribute
        values containing `"filter"`:

        ```python
        find_link("partial_href", "filter")
        ```

        Arguments/return value:

        `ltype`: The link selector type.

        `lval`: The value of the link selector type.

        `return`: A list of matching link elements.

        """        

        # The implementation of the action
        def find_link(ltype: LinkActionType, lval: str) -> ElementList:
            return self._api_map["link"][ltype](lval)

        # Return the action
        return find_link
    
    @webaction
    def _mk_element_click_link(self) -> ActionFunc:
        R"""Action `element_click_link` clicks the link

        Click on the link element.

        Arguments/return value:

        `element`: A list of the web elements.

        `index`: Choose from the list of elements (default 0).

        """

        # The implementation of the action
        def element_click_link(element: ElementList, index: int = 0):
            element = _prep_element(element)
            element[index].click()

        # Return the action
        return element_click_link
    
    @webaction
    def _mk_click_link(self) -> ActionFunc:
        R"""Action `click_link` clicks a link

        Click on a link element matching the selector `ltype` with the
        value `lval`. This example clicks on a link element with the
        partial text `"news"`:

        ```python
        click_link("partial_text", "news")
        ```

        Arguments/return value:

        `ltype`: The link selector type.

        `lval`: The value of the link selector type.

        `index`: Choose from the list of matching elements (default 0).

        """

        # The implementation of the action
        def click_link(ltype: LinkActionType, lval: str, index: int = 0):
            self._api_map["link"][ltype](lval)[index].click()

        # Return the action
        return click_link

    @webaction
    def _mk_is_present(self) -> ActionFunc:
        R"""Action `is_present` checks if a web element is present

        The action `is_present` checks if a web element based on a
        selector type and the value of such a selector is present.
        This example returns `True` if a web element with id `"news"`
        is present:

        ```python
        is_present("id", "news")
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `wait_time`: How long to wait for the web element to be
        present (default `None`).

        `return`: Returns True if the web element is present.

        """

        # The implementation of the action
        def is_present(
                stype: SelectorType,
                sval: str,
                wait_time: int | None = None) -> bool:
            if stype in self._api_map["is_element_present"]:
                return self._api_map["is_element_present"][stype](
                    sval, wait_time=wait_time)
            else:
                raise WebInteractionError(
                    f'Action is_element_present failed: ' + \
                    f'Unknown element type: {stype}\n')

        # Return the action
        return is_present
    
    @webaction
    def _mk_is_not_present(self) -> ActionFunc:
        R"""Action `is_not_present` checks if a web element is not present

        The action `is_not_present` checks if a web element based on
        the selector type `stype` with the value `sval` is not
        present. This example returns `True` if a web element with
        name `"loginform"` is not present:

        ```python
        is_not_present("name", "loginform")
        ```
        
        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `wait_time`: How long to wait for the web element to be
        present (default `None`)

        `return`: Returns True if the web element is not present.

        """

        # The implementation of the action
        def is_not_present(
                stype: SelectorType,
                sval: str,
                wait_time: int | None = None) -> bool:
            if stype in self._api_map["is_element_not_present"]:
                return self._api_map["is_element_not_present"][stype](
                    sval, wait_time=wait_time)
            else:
                raise WebInteractionError(
                    f'Action is_element_not_present failed: ' + \
                    f'Unknown element type: {stype}\n')

        # Return the action
        return is_not_present
    
    @webaction
    def _mk_is_text_present(self) -> ActionFunc:
        R"""Action `is_text_present` checks if a text is present

        The action `is_text_present` checks if the text is
        present. This example returns `True` if the text `"Login
        succeeded"` is present within 3 seconds:

        ```python
        is_text_present("Login succeeded", 3)
        ```

        Arguments/return value:

        `text`: The text to find.

        `wait_time`: How long to wait for the text to be present
        (default `None`).

        `return`: Returns `True` if the text is present.

        """
        
        # The implementation of the action
        def is_text_present(
                text: str,
                wait_time: int | None = None) -> bool:
            return self._browser.is_text_present(text, wait_time)

        # Return the action
        return is_text_present

    @webaction
    def _mk_is_text_not_present(self) -> ActionFunc:
        R"""Action `is_text_present` checks if a text is not present

        The action `is_text_not_present` checks if the text is not
        present. This example returns `True` if the text `"Login
        failed"` is not present:

        ```python
        is_text_not_present("Login failed")
        ```

        Arguments/return value:

        `text`: The text that should't be present.

        `wait_time`: How long to wait for the text to be present
        (default `None`).

        `return`: Returns `True` if the text is not present.

        """

        # The implementation of the action
        def is_text_not_present(
                text: str,
                wait_time: int | None = None) -> bool:
            return not self._browser.is_text_present(text, wait_time)

        # Return the action
        return is_text_not_present

    @webaction
    def _mk_element_attach_file(self) -> ActionFunc:
        R"""Action `element_attach_file` attachs a file to the web element

        Attach a file to the web element (a file input element).

        Arguments/return value:

        `file_path`: Absolute path to file.
        
        `element`: A list of the web elements.

        `index`: Choose from the list of matching elements (default `None`).

        """

        # The implementation of the action
        def attach_file(element: ElementList, index: int | None = None):
            _element_action_it(element, index, "fill", file_path)
        
        # Return the action
        return attach_file

    @webaction
    def _mk_attach_file(self) -> ActionFunc:
        R"""Action `attach_file` attachs a file to a web element

        Attach a file to a web element (a file input element).  In
        this example, the file `"/path/to/file"` is attached to a web
        element with the name `"thefile"`:

        ```python
        attach_file("/path/to/file", "name", "thefile")
        ```

        Arguments/return value:

        `file_path`: Absolute path to file.
        
        `stype`: The selector type.

        `sval`: The value of the selector type.

        `index`: Choose from the list of matching elements (default `None`).

        """

        # The implementation of the action
        def attach_file(
                file_path: str,
                stype: SelectorType, sval: str, index: int | None = None):
            element = self._do_find(stype, sval)
            _element_action_it(element, index, "fill", file_path)
        
        # Return the action
        return attach_file

    @webaction
    def _mk_element_doall(self) -> ActionFunc:
        R"""Do action on all elements of list of the web elements

        Do the same action on all web elements in the web element
        list. In this example, all chekboxes on a web page are
        checked:

        ```python
        element_doall( \
          find("xpath", "//input[@type='checkbox']"), element_check)
        ```

        Arguments/return value:

        `elements`: A list of the web elements.

        `action`: The action performed on each element.

        `*args`: Arguments to the action.

        `**kw`: Keyword arguments to the action.

        `return`: The aggregated result of all actions or None.

        """

        # The implementation of the action
        def element_doall(
                elements: ElementList,
                action: ActionFunc,
                *args: tuple, sep: str = "\n", **kw: dict) -> str | None:
            elements = _prep_element(elements)
            kw['element'] = elements
            result = ""
            for i in range(len(elements)):
                kw['index'] = i
                r =  _do_inline_action(action(*args, **kw))
                if r:
                    if result:
                        result += sep
                    result += r
            if result: return result

        # Return the action
        return element_doall
    
    @webaction
    def _mk_doall(self) -> ActionFunc:
        R"""Do action on all elements of list of web elements

        Do the same action on all web elements in the web element
        list. In this example, the value of all select elements on a
        web page are fetched:

        ```python
        doall("tag", "select", element_get_value)
        ```

        Arguments/return value:

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `action`: The action performed on each element.

        `*args`: Arguments to the action.

        `sep`: A separator inserted between each of result returned if
        the action returns a result (default `"\n"`)

        `**kw`: Keyword arguments to the action.

        `return`: The aggregated result of all actions or None.

        """

        # The implementation of the action
        def doall(
                stype: SelectorType, sval: str,
                action: ActionFunc,
                *args: tuple, sep: str = "\n", **kw: dict) -> str | None:
            #elements = _prep_element(self._do_find(stype, sval))
            elements = self._do_find(stype, sval)
            kw['element'] = elements
            result = ""
            for i in range(len(elements)):
                kw['index'] = i
                r =  _do_inline_action(action(*args, **kw))
                if r:
                    if result:
                        result += sep
                    result += r
            if result: return result

        # Return the action
        return doall

    @webaction
    def _mk_element_cond(self) -> ActionFunc:
        R"""Do action on the web element if condition is true

        Do `ifaction` if condition is true. If provided, do elseaction
        if condition is false.  This example unchecks the checkbox
        element `checkbox1` if it is checked, and checks if it is
        unchecked (a checkbox toggle):

        ```python
        element_cond( \
          verify(element_get_value(checkbox1), "on", assert_it = False), \
          checkbox1, ifaction = element_uncheck, elseaction = element_check)
        ```
        
        Arguments/return value:

        `condition`: The condition.

        `element`: A list of the web elements.

        `ifaction`: The action performed if condition is true.

        `*args`: Arguments to the action (both `ifaction` and `elseaction`).

        `elseaction`: The action performed if condition is false
        (default `None`).

        `index`: Choose from the list of matching elements (default 0).
        
        `**kw`: Keyword arguments to the action (both `ifaction` and
        `elseaction`).

        `return`: The aggregated result of all actions or None.

        """

        # The implementation of the action
        def element_cond(
                condition: bool,
                element: ElementList,
                ifaction: ActionFunc,
                *args: tuple,
                elseaction: ActionFunc = None,
                index: int = 0, **kw: dict) -> str | None:
            condition = _prep_element(condition)
            kw['element'] = _prep_element(element)
            kw['index'] = index
            if condition:
                return _do_inline_action(ifaction(*args, **kw))
            elif elseaction:
                return _do_inline_action(elseaction(*args, **kw))

        # Return the action
        return element_cond
    
    @webaction
    def _mk_cond(self) -> ActionFunc:
        R"""Do action a web element if condition is true

        Do `ifaction` if condition is true. If provided, do elseaction
        if condition is false.  This example unchecks the checkbox
        element `checkbox1` if it is checked, and checks if it is
        unchecked (a checkbox toggle):

        ```python
        cond( \
          verify(element_get_value(checkbox1), "on", assert_it = False), \
          "name", "checkbox1", \
          ifaction = element_uncheck, elseaction = element_check)
        ```

        Arguments/return value:

        `condition`: The condition.

        `stype`: The selector type.

        `sval`: The value of the selector type.

        `ifaction`: The action performed if condition is true.

        `*args`: Arguments to the action (both `ifaction` and `elseaction`).

        `elseaction`: The action performed if condition is false
        (default `None`).

        `index`: Choose from the list of matching elements (default 0).
        
        `**kw`: Keyword arguments to the action (both `ifaction` and
        `elseaction`).

        `return`: The aggregated result of all actions or None.

        """

        # The implementation of the action
        def cond(
                condition: bool,
                stype: SelectorType, sval: str,
                ifaction: ActionFunc,
                *args: tuple,
                elseaction: ActionFunc = None,
                index: int = 0, **kw: dict) -> str | None:
            condition = _prep_element(condition)
            kw['element'] = self._do_find(stype, sval)
            kw['index'] = index
            if condition:
                return _do_inline_action(ifaction(*args, **kw))
            elif elseaction:
                return _do_inline_action(elseaction(*args, **kw))

        # Return the action
        return cond

    
#
# More help functions (to produce documentation)
#
    
def _insert_sig_in_doc(
        method: Callable,
        doc: str | None = None,
        name: str | None = None,
        clsname: str = "") -> str:
    R"""Insert the signature of the method into method documentation

    The function modifies the documentation string by inserting the
    signature of the method. The modified documentation string is
    returned.

    Arguments/return value:

    `method`: The method

    `doc`: The documentation string of the method (optional, grap the
    documentation string from the method if it is not provided)

    `name`: The name of the method (optional, grap the name of the
    method from the method itself if it is not provided)

    `clsname`: The class name (optional)
    
    `return`: Modified documentation string

    """
    if not doc: doc = method.__doc__
    doc_lines = doc.splitlines()
    sig = str(signature(method))
    if ", " in sig:
        sig = sig.replace("self, ", "", 1)
    else:
        sig = sig.replace("self", "", 1)
    if not name: name = method.__name__
    if clsname:
        clsname += "."
        ttxt = "Method"
    else:
        ttxt = "Class"
    res = f"{ttxt} `{clsname}{name}`\n"
    res += f"\n`{name}{sig}`\n\n*{doc_lines[0]}*\n"
    res += "\n".join(doc_lines[1:])
    return res


def _get_action_name_and_sig(mkf: MakeActionFunc) -> tuple[str, str]:
    R"""Get the name and signature of an action

    Get the name and the signature of an action by using the method
    making the action and then grap this information from the action
    itself.
    
    Arguments/return value:

    `mkf`: Method making the specific action

    `return`: A two-tuple with the name and signature of the action

    """
    f = mkf(None)
    fname = f["name"]
    fsig = str(signature(f["action"]))
    return fname, fsig


def _get_actions() -> ActionInfoMap:
    R"""Get information about all actions

    Get the information about all actions, including their name,
    signature, the method making the action, and the qualified name of
    the method making the action.

    Return value:

    `return`: A dictionary where the key is the action name and the
    content of each item is another dictionary with the information
    about that action.

    """

    # Traverse the complete content of the `WebInteraction` class
    actions = {}
    for a in dir(WebInteraction):

        # If this is a method making an action
        if a[:4] == '_mk_':

            # Get the method
            mkf = getattr(WebInteraction, a)

            # Check that it is not deprecated
            if mkf.__doc__[:10] == "DEPRECATED":
                continue

            # Get the name of the action and its signature
            fname, fsig = _get_action_name_and_sig(mkf)

            # Use the name as a key to a dictionary item with the
            # method making the action, the signature of the action
            # and the qualified name of the method making the action
            actions[fname] = {
                "mkf": mkf,
                "sig": fsig,
                "mk_name": mkf.__qualname__}

    # Return the information about all actions
    return actions


def _make_docs() -> dict[str, str]:
    """Create action documentation

    Traverese the `WebInteraction` class for each action and generates
    its documentation.

    Return value:

    `return`: A dictionary with the documentation of each named action

    """
    docs = {}
    for fname, finfo in _get_actions().items():
        docs[fname] = fname + finfo["sig"] + "\n\n"
        docs[fname] += finfo["mkf"].__doc__.strip()
    return docs

def _action_list(mk_name: bool = True) -> list:
    R"""List all names of the actions

    List all names of the actions, and ensure that the actions related
    are neigbours in the list.

    Arguments/return value:

    `mk_name`: If `mk_name` is `True` the names in the list is the
    qualified names of the methods making the actions, and not the
    name of the actions them self (default `True`)

    `return`: A list of the names of all actions (or the qualified
    name of the methods making the actions)

    """

    # get all actions
    actions = _get_actions()

    # Should we return the action names or the qualified name of the
    # methods making the actions
    if mk_name:
        get_name = lambda a: actions[a]["mk_name"]
    else:
        get_name = lambda a: a

    # First, list all names that does not start with `"element_"`
    action_names = actions.keys()
    main_a = [k for k in filter(lambda x: not "element_" in x, action_names)]

    # Then insert the names that start with `"element_"` at the right position
    action_list = []
    for a in main_a:
        action_list.append(get_name(a))
        if f"element_{a}" in action_names:
            action_list.append(get_name(f"element_{a}"))

    # Return the list of names
    return action_list
 
def _list_actions(docs, sep: str = "\n", pre: str = "") -> str:
    R"""List all actions

    List all action name in a text string, one action per line.

    Arguments/return value:

    `sep`: The separator between each action name (default a new line, `"\n"`)

    `pre`: A string put in front of each name (default the empty string `""`)

    `return`: The text string with all the action names

    """
    actions = _action_list(mk_name = False)
    return sep.join([pre + key for key in actions])


################################################################################
#
# Use the module as a program (to perform a web interaction script)
#
# Usage: webinteract [-h] [-V] [-n NAME_SPACE] [-s PW_SERVICE] [-a PW_ACCOUNT]
#                    [-o OUTPUT_FILE_NAME] [--driver DRIVER] [--headless]
#                    [--keep] [--prompt PROMPT] [--prompt-color PROMPT_COLOR]
#                    [--prompt-output-color PROMPT_OUTPUT_COLOR]
#                    [--prompt-alert-color PROMPT_ALERT_COLOR]
#                    [script]
#
# Perform a web interaction action script.
#
# Positional arguments:
#   script                The web script file name (path), '-' for stdin
#
# Options:
#   -h, --help            Show this help message and exit
#   -V, --version         Show program's version number and exit
#   -D, --doc [ACTION]    Print documentation of module or specific action
#   -n, --name-space NAME_SPACE
#                         Add variables to name space (json)
#   -s, --pw-service PW_SERVICE
#                         Password stored at this service name in keychain
#   -a, --pw-account PW_ACCOUNT
#                         Password stored at this account name in keychain
#   -o, --output-file OUTPUT_FILE_NAME
#                         Any output is written to this file (default stdout)
#   --driver DRIVER       The web interaction driver name
#   --headless            Run browser headless (invisible)
#   --keep                Keep browser running after script has terminated
#   --prompt PROMPT       The text of the interactive prompt
#   --prompt-color PROMPT_COLOR
#                         The text color of the interactive prompt
#   --prompt-output-color PROMPT_OUTPUT_COLOR
#                         The text color of the interactive output
#   --prompt-alert-color PROMPT_ALERT_COLOR
#                         The text color of the interactive alerts
# 
################################################################################


def main():
    """Run module as a program

    Run the module as a program, either interpreting a given wia
    script or with a command prompt.

    """

    # Needs these modules
    import traceback

    # Create argument parser
    import argparse, json
    parser = argparse.ArgumentParser(
        description="Perform a web interaction action script.")
    parser.add_argument("-V", "--version", action="version",
                        version=f"%(prog)s " + version)
    parser.add_argument("-D", "--doc", nargs='?', metavar="ACTION",
                        const=True, default=None,
                        help="print documentation of module or specific action")
    parser.add_argument("-d", "--doc-noactions", action="store_true",
                        default=False, help=argparse.SUPPRESS)
    parser.add_argument("-L", "--list-actions", nargs='?', metavar="ACTION",
                        const=True, default=None, help=argparse.SUPPRESS)
    parser.add_argument("-M", "--list-methods", nargs='?', metavar="METHOD",
                        const=True, default=None, help=argparse.SUPPRESS)
    parser.add_argument("-n", "--name-space", type=json.loads,
                        help="add variables to name space (json)")
    parser.add_argument("-s", "--pw-service",
                        help="password stored at this service name in keychain")
    parser.add_argument("-a", "--pw-account",
                        help="password stored at this account name in keychain")
    parser.add_argument("-o", "--output-file", dest="output_file_name",
                        help="any output is written to this file " +
                        "(default stdout)")
    parser.add_argument("--driver", default=None,
                        help="the web interaction driver name")
    parser.add_argument("--headless", action="store_true",
                        help="run browser headless (invisible)")
    parser.add_argument("--keep", action="store_true",
                        help="keep browser running after script has terminated")
    parser.add_argument("--prompt", default="wia> ",
                        help="the text of the interactive prompt")
    parser.add_argument("--prompt-color", default="LIGHTYELLOW_EX",
                        help="the text color of the interactive prompt")
    parser.add_argument("--prompt-output-color", default="GREEN",
                        help="the text color of the interactive output")
    parser.add_argument("--prompt-alert-color", default="LIGHTRED_EX",
                        help="the text color of the interactive alerts")
    parser.add_argument("script", nargs='?',
                        help="the web script file name (path), '-' for stdin")
    
    # Parse arguments
    args = parser.parse_args()

    # List all web actions (for internal usage)
    if args.list_actions:
        docs = _make_docs()
        if args.list_actions == True:
            print(_list_actions(docs))
        elif args.list_actions in docs:
            fname, fsig = _get_action_name_and_sig(
                getattr(WebInteraction, "_mk_" + args.list_actions))
            print(fname + fsig)
        else:
            print(f"List actions: Unknown action '{args.list_actions}'")
            sys.exit(1)
        return

    # List `WebInteraction` methods
    _methods = ["WebInteraction", "update", "execute", "quit"]
    if args.list_methods:
        if args.list_methods == True:
            print("\n".join(_methods))
        elif args.list_methods in _methods:
            if args.list_methods == "WebInteraction":
                _m = getattr(WebInteraction, "__init__")
            else:
                _m = getattr(WebInteraction, args.list_methods)
            sig = str(signature(_m))
            # Remove "self"
            if ", " in sig: 
                sig = sig.replace("self, ", "", 1)
            else:
                sig = sig.replace("self", "", 1)
            print(args.list_methods + sig)
        else:
            print(f"List methods: Unknown method '{args.list_methods}'")
            sys.exit(1)
        return
    
    # Print documentation?
    if args.doc_noactions: args.doc = True
    if args.doc:
        docs = _make_docs()
        if args.doc == True:
            print('\n' + __doc__.strip() + '\n')
            print(_insert_sig_in_doc(
                WebInteraction.__init__,
                WebInteraction.__doc__,
                "WebInteraction"))
            print("\n".join(WebInteraction.__init__.__doc__.splitlines()[2:]))
            for _m in _methods[1:]:
                print(_insert_sig_in_doc(
                    getattr(WebInteraction, _m),
                    clsname="WebInteraction"))
            if not args.doc_noactions:
                print("All available web actions:\n")
                print(_list_actions(docs, pre=" - ") + '\n')
        elif args.doc in docs:
            print('\n' + docs[args.doc] + '\n')
        else:
            print(f"Print documentation: Unknown action '{args.doc}'")
        return

    # Create and update name space from arguments
    ns = {}
    if args.name_space:
        ns.update(args.name_space)

    # Open output file
    if args.output_file_name:
        args.output_file = open(args.output_file_name, "w")
    else:
        args.output_file = sys.stdout

    # Get password from keychain?
    if args.pw_account or args.pw_service:
        if args.pw_account and args.pw_service:
            import keyring
            if "pw_service" not in ns:
                ns["pw_service"] = args.pw_service
            if "pw_account" not in ns:
                ns["pw_account"] = args.pw_account
            ns["pw"] = keyring.get_password(args.pw_service, args.pw_account)
            if not ns["pw"]:
                raise LookupError(
                    f"Didn't find pw for {args.pw_account} in keychain")
        else:
            raise LookupError(
                f"Needs both --pw-service and --pw-account to fetch pw")

    # Perform the web interaction
    try:

        # Create the keyword arguments to `WebInteraction` class
        # (equal to the `Browser` class of `splinter`)
        kw = {"headless": args.headless}
        if args.driver:
            kw["driver_name"] = args.driver

        # Create the web interaction object
        web_interaction = WebInteraction(**kw)

        # Update the namespace of the web interaction script
        web_interaction.update(ns)

        # Perform the script in the file with file name args.script
        if args.script and args.script != "-":
            input = open(args.script)
        else:
            input = None
        web_interaction(input, vars(args))
        
    # Something else failed in the web-page interaction
    except Exception as err:
        msg = f"Web page interaction failed: {err}\n"
        msg += "".join(traceback.format_exception(*sys.exc_info()))
        raise WebInteractionError(msg)

    # Quit browser (if it was successfully launched)
    if not args.keep:
        try:
            web_interaction.quit()
        except:
            pass


# Execute this module as a program
if __name__ == '__main__':
    main()
