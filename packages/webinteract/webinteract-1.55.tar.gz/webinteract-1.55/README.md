<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


### <a id="module-webinteract"></a>The `webinteract` module for simple web interaction

The blog post [Web page interaction in
Python](https://blog.pg12.org/web-page-interaction-in-python) provides
a more complete documentation of the `webinteract` module. See
[PyPi](https://pypi.org/project/webinteract/) for an up-to-date (but
not detailed) documentation generated from the source code of the
module.

To-do (planned):

 - Better error handling and improved error messages
 - Better support for data harvesting

**<a id="Table+of+contents"></a>Table of contents**

 - [To install and use the module](#install)
 - [Class `WebInteraction`](#webinteraction1)
     - [Initialize `WebInteraction`](#Initialize+%60WebInter)
     - [Method `WebInteraction.update`](#webinteraction.upda1)
     - [Method `WebInteraction.execute`](#webinteraction.exec1)
     - [Method `WebInteraction.quit`](#webinteraction.quit1)
 - [Console script command line arguments](#console-script)
     - [Command `webinteract`](#Command+%60webinteract)
 - [All `webinteract` web actions documented](#All+%60webinteract%60+we)

### <a id="install"></a>To install and use the module

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
import webinteract                      # This module

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



### <a id="webinteraction1"></a>Class `WebInteraction`

*The web interaction class for web sessions*

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



#### <a id="Initialize+%60WebInter"></a>Initialize `WebInteraction`

```python
WebInteraction(*args: tuple, **kw: dict)
```

*Instanciate a web interaction object*

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

**Arguments:**

`*args`: positional arguments to the the `Browser` constructor

`**kw`: named arguments to the the `Browser` constructor



#### <a id="webinteraction.upda1"></a>Method `WebInteraction.update`

```python
update(*args: tuple[dict[str, typing.Any]], **kw: dict[str, typing.Any])
```

*Update the namespace*

Update the web interaction action namespace with variables
that can be used in the scripts (typically values used as
arguments to the fuctions that can not be specified directly
in the scripts). If `web` is a `WebInteraction` instance,
these two `update` calls perform the same update:

```python
web.update({"pw": "a s3cret p4ssw0rd", "date": ts})
web.update(pw = "a s3cret p4ssw0rd", date = ts)
```

**Arguments:**

`*args`: positional arguments, name space (dictionary)
mapping names to values.

`**kw`: named arguments, mapping names to values



#### <a id="webinteraction.exec1"></a>Method `WebInteraction.execute`

```python
execute(file: typing.TextIO | None = None, args_dict: dict | None = None)
```

*Read and and execute the web interaction action script*

This perform the actual execution of the web interaction
action script using the web interaction action language
defined by the functions in the web interaction action name
space.

This method is called when an instance of the `WebInteraction`
class is called like a function.

**Arguments:**

`file`: The file object with the web interaction action script
(any object implementing Python text i/o will do:
https://docs.python.org/3/library/io.html). If this is `None`,
read web interaction actions from a prompt.



#### <a id="webinteraction.quit1"></a>Method `WebInteraction.quit`

```python
quit()
```

*Quit the browser*

Quit the browser and terminate the web interaction session.



### <a id="console-script"></a>Console script command line arguments


#### <a id="Command+%60webinteract"></a>Command `webinteract`


*Perform a web interaction action script.*

**Usage:**

```bash
webinteract [-h] [-V] [-D [ACTION]] [-n NAME_SPACE] [-s PW_SERVICE] [-a PW_ACCOUNT] [-o OUTPUT_FILE_NAME] [--driver DRIVER] [--headless] [--keep] [--prompt PROMPT] [--prompt-color PROMPT_COLOR] [--prompt-output-color PROMPT_OUTPUT_COLOR] [--prompt-alert-color PROMPT_ALERT_COLOR] [script]
```

**Positional arguments:**

Name | Description
---- | -----------
`script` | the web script file name (path), `-` for stdin

**Options:**

Name | Description
---- | -----------
`-h, --help` | show this help message and exit
`-V, --version` | show program's version number and exit
`-D, --doc [ACTION]` | print documentation of module or specific action
`-n, --name-space NAME_SPACE` | add variables to name space (json)
`-s, --pw-service PW_SERVICE` | password stored at this service name in keychain
`-a, --pw-account PW_ACCOUNT` | password stored at this account name in keychain
`-o, --output-file OUTPUT_FILE_NAME` | any output is written to this file (default stdout)
`--driver DRIVER` | the web interaction driver name
`--headless` | run browser headless (invisible)
`--keep` | keep browser running after script has terminated
`--prompt PROMPT` | the text of the interactive prompt
`--prompt-color PROMPT_COLOR` | the text color of the interactive prompt
`--prompt-output-color PROMPT_OUTPUT_COLOR` | the text color of the interactive output
`--prompt-alert-color PROMPT_ALERT_COLOR` | the text color of the interactive alerts


### <a id="All+%60webinteract%60+we"></a>All `webinteract` web actions documented


The web action index:
[attach_file](#attach_file), [element_attach_file](#element_attach_file), [check](#check), [element_check](#element_check), [clear](#clear), [element_clear](#element_clear), [click](#click), [element_click](#element_click), [click_link](#click_link), [element_click_link](#element_click_link), [cond](#cond), [element_cond](#element_cond), [dialog](#dialog), [doall](#doall), [element_doall](#element_doall), [fill](#fill), [element_fill](#element_fill), [find](#find), [find_in_element](#find_in_element), [find_link](#find_link), [get](#get), [element_get](#element_get), [get_text](#get_text), [element_get_text](#element_get_text), [get_value](#get_value), [element_get_value](#element_get_value), [is_checked](#is_checked), [element_is_checked](#element_is_checked), [is_not_present](#is_not_present), [is_present](#is_present), [is_text_not_present](#is_text_not_present), [is_text_present](#is_text_present), [scroll_to](#scroll_to), [element_scroll_to](#element_scroll_to), [select](#select), [element_select](#element_select), [setvals](#setvals), [uncheck](#uncheck), [element_uncheck](#element_uncheck), [verify](#verify), [visit](#visit), [wait](#wait)
<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="attach_file"></a>attach_file


```python
attach_file(file_path: str, stype: SelectorType, sval: str, index: int | None = None)
```

*Action `attach_file` attachs a file to a web element*

Attach a file to a web element (a file input element).  In
this example, the file `"/path/to/file"` is attached to a web
element with the name `"thefile"`:

```python
attach_file("/path/to/file", "name", "thefile")
```

**Arguments/return value:**

`file_path`: Absolute path to file.

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default `None`).


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_attach_file"></a>element_attach_file


```python
element_attach_file(element: splinter.element_list.ElementList, index: int | None = None)
```

*Action `element_attach_file` attachs a file to the web element*

Attach a file to the web element (a file input element).

**Arguments/return value:**

`file_path`: Absolute path to file.

`element`: A list of the web elements.

`index`: Choose from the list of matching elements (default `None`).


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="check"></a>check


```python
check(stype: SelectorType, sval: str, index: int | None = None, doall: bool = False)
```

*Action `check` checks a web element (checkbox)*

Check a checkbox web element matching the selector `stype`
with the value `sval`. This example checks the fourth checkbox
on the web page (with index 3):

```python
check("xpath", "//input[@type='checkbox']", 3)
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_check"></a>element_check


```python
element_check(element: splinter.element_list.ElementList, index: int | None = None, doall: bool = False)
```

*Action `element_check` checks the web element (checkbox)*

Check the checkbox web element.

**Arguments/return value:**

`element`:  A list of the web elements.

`index`: Choose from the list of elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="clear"></a>clear


```python
clear(stype: SelectorType, sval: str, index: int | None = None, doall: bool = False)
```

*Action `clear` clears a web element*

Reset the field value of a web element matching the selector
`stype` with the value `sval`. This example clears a field
with the name `"search"`:

```python
clear("name", "search")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_clear"></a>element_clear


```python
element_clear(element: splinter.element_list.ElementList, index: int | None = None, doall: bool = False)
```

*Action `element_clear` clears the web element*

Reset the field value of the web element.

**Arguments/return value:**

`element`:  A list of the web elements.

`index`: Choose from the list of elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="click"></a>click


```python
click(stype: SelectorType, sval: str, index: int | None = None)
```

*Action `click` clicks a web element (button)*

Click on a web element matching the selector `stype` with the
value `sval`. This example clicks on a web element with the
text `"OK"` (typically a button):

```python
click("text", "OK")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default `None`).


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_click"></a>element_click


```python
element_click(element: splinter.element_list.ElementList, index: int | None = None)
```

*Action `element_click` clicks the web element (button)*

Click on the web element.

**Arguments/return value:**

`element`: A list of the web elements.

`index`: Choose from the list of elements (default `None`).


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="click_link"></a>click_link


```python
click_link(ltype: LinkActionType, lval: str, index: int = 0)
```

*Action `click_link` clicks a link*

Click on a link element matching the selector `ltype` with the
value `lval`. This example clicks on a link element with the
partial text `"news"`:

```python
click_link("partial_text", "news")
```

**Arguments/return value:**

`ltype`: The link selector type.

`lval`: The value of the link selector type.

`index`: Choose from the list of matching elements (default 0).


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_click_link"></a>element_click_link


```python
element_click_link(element: splinter.element_list.ElementList, index: int = 0)
```

*Action `element_click_link` clicks the link*

Click on the link element.

**Arguments/return value:**

`element`: A list of the web elements.

`index`: Choose from the list of elements (default 0).


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="cond"></a>cond


```python
cond(condition: bool, stype: SelectorType, sval: str, ifaction: ActionFunc, *args: tuple, elseaction: ActionFunc = None, index: int = 0, **kw: dict) -> str | None
```

*Do action a web element if condition is true*

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

**Arguments/return value:**

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


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_cond"></a>element_cond


```python
element_cond(condition: bool, element: splinter.element_list.ElementList, ifaction: ActionFunc, *args: tuple, elseaction: ActionFunc = None, index: int = 0, **kw: dict) -> str | None
```

*Do action on the web element if condition is true*

Do `ifaction` if condition is true. If provided, do elseaction
if condition is false.  This example unchecks the checkbox
element `checkbox1` if it is checked, and checks if it is
unchecked (a checkbox toggle):

```python
element_cond( \
  verify(element_get_value(checkbox1), "on", assert_it = False), \
  checkbox1, ifaction = element_uncheck, elseaction = element_check)
```

**Arguments/return value:**

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


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="dialog"></a>dialog


```python
dialog(dialog_text: str = '', **kw)
```

*Action `dialog` set values from user input*

The `dialog` action is a way for a `wia` script to get input
from the user (or block the execution of the script until the
user gives some input).  This example provides a short
description and set the values of `user` and `age` in the name
space:

```python
dialog("Please set user and age", user="User", age="Age")
```

This example presents a short description and blocks the script
until the user presses return (no values are set):

```python
dialog("Check the filled in form and press return to submit")
```

**Arguments:**

`dialog_text`: A description of the expected input (default "",
meaning the description is not presented).

`kw`: Named arguments that describes values in the namespace
for each input from the user.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="doall"></a>doall


```python
doall(stype: SelectorType, sval: str, action: ActionFunc, *args: tuple, sep: str = '\n', **kw: dict) -> str | None
```

*Do action on all elements of list of web elements*

Do the same action on all web elements in the web element
list. In this example, the value of all select elements on a
web page are fetched:

```python
doall("tag", "select", element_get_value)
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`action`: The action performed on each element.

`*args`: Arguments to the action.

`sep`: A separator inserted between each of result returned if
the action returns a result (default `"\n"`)

`**kw`: Keyword arguments to the action.

`return`: The aggregated result of all actions or None.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_doall"></a>element_doall


```python
element_doall(elements: splinter.element_list.ElementList, action: ActionFunc, *args: tuple, sep: str = '\n', **kw: dict) -> str | None
```

*Do action on all elements of list of the web elements*

Do the same action on all web elements in the web element
list. In this example, all chekboxes on a web page are
checked:

```python
element_doall( \
  find("xpath", "//input[@type='checkbox']"), element_check)
```

**Arguments/return value:**

`elements`: A list of the web elements.

`action`: The action performed on each element.

`*args`: Arguments to the action.

`**kw`: Keyword arguments to the action.

`return`: The aggregated result of all actions or None.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="fill"></a>fill


```python
fill(val: str, stype: SelectorType, sval: str, index: int | None = None, doall: bool = False)
```

*Action `fill` fills the value in a web element*

Fill in the value `val` in a web element matching the selector
`stype` with the value `sval`. In this example, a web element with
the name `"search"` is filled with the text `"Python"`:

```python
fill("Python", "name", "search")
```

**Arguments/return value:**

`val`: The value to fill-in.

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_fill"></a>element_fill


```python
element_fill(val: str, element: splinter.element_list.ElementList, index: int | None = None, doall: bool = False)
```

*Action `element_fill` fills the value in the element*

Fill in the value `val` in the web element.

**Arguments/return value:**

`val`: The value to fill-in.

`element`: A list of the web elements.

`index`: Choose from the list of elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="find"></a>find


```python
find(stype: SelectorType, sval: str) -> splinter.element_list.ElementList
```

*Action `find` finds web elements on a web page*

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

**Arguments/return value:**

`stype`: The selector type (either `"css"`, `"id"`, `"name"`,
`"tag"`, `"text"`, `"value"`, or `"xpath"`).

`sval`: The value of the selector type.

`return`: A list of the web elements matching the selector
`stype` with the value `sval`.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="find_in_element"></a>find_in_element


```python
find_in_element(stype: SelectorType, sval: str, element: splinter.element_list.ElementList, index: int = 0) -> splinter.element_list.ElementList
```

*Action `find_in_element` finds web elements inside the web element*

This action finds web elements based on a selector type and
the value of such a selector inside the given web
element. This example returns a list of web elements with the
name `"filter"` from inside a web element with the id
`"form"`:

```python
find_in_element("name", "filter", find("id", "form"), 0)
```

**Arguments/return value:**

`stype`: The selector type (either `"css"`, `"id"`, `"name"`,
`"tag"`, `"text"`, `"value"`, or `"xpath"`).

`sval`: The value of the selector type.

`element`: Find the web element inside one of these elements.

`index`: Choose from the list of elements (default 0).        

`return`: A list of the web elements matching the selector
`stype` with the value `sval`.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="find_link"></a>find_link


```python
find_link(ltype: LinkActionType, lval: str) -> splinter.element_list.ElementList
```

*Action `find_link` finds link elements*

The action `find_link` returns link web elements based on a
link selector type and the value of such a link selector. This
example returns a list of link elements with `href` attribute
values containing `"filter"`:

```python
find_link("partial_href", "filter")
```

**Arguments/return value:**

`ltype`: The link selector type.

`lval`: The value of the link selector type.

`return`: A list of matching link elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="get"></a>get


```python
get(stype: SelectorType, sval: str, index: int = 0) -> str
```

*Action `get` gets the value or text of a web element*

Get the value or text of a web element matching the selector
`stype` with the value `sval`. An example where we get the
value or text of an element with the id `"about"`:

```python
get("id", "about")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default 0).

`return`: The value or text of a web element matching the
selector `stype` with the value `sval`.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_get"></a>element_get


```python
element_get(element: splinter.element_list.ElementList, index: int = 0) -> str
```

*Action `element_get` gets the value or text of the web element*

Get the value or text of the given web element.

**Arguments/return value:**

`element`: A list of the web elements.

`index`: Choose from the list of matching elements (default 0).

`return`: The value or text of a web element.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="get_text"></a>get_text


```python
get_text(stype: SelectorType, sval: str, index: int = 0) -> str
```

*Action `get_text` gets the text of a web element*

Get the text of a web element matching the selector stype with
the value sval. An example where we get the text of the third
element (at index 2) with the tag `"h2"`:

```python
get_text("tag", "h2", 2)
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default 0).

`return`: The text of a web elements matching the selector
`stype` with the value `sval`.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_get_text"></a>element_get_text


```python
element_get_text(element: splinter.element_list.ElementList, index: int = 0) -> str
```

*Action `element_get_text` gets the text of the web element*

Returns true if te web element is checked.

**Arguments/return value:**

`element`:  A list of the web elements.

`index`: Choose from the list of elements (default 0).

`return`: The text of the web element.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="get_value"></a>get_value


```python
get_value(stype: SelectorType, sval: str, index: int = 0) -> str
```

*Create action `get_value` gets the value of a web element*

Get the value of a web element matching the selector stype
with the value sval. An example where we get the value of an
element with the name `"aggregate"`:

```python
get_value("name", "aggregate")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default 0).

`return`: The value of a web elements matching the selector
`stype` with the value `sval`.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_get_value"></a>element_get_value


```python
element_get_value(element: splinter.element_list.ElementList, index: int = 0) -> str
```

*Action `element_get_value` gets the value of the web element*

Get the value of the web element.

**Arguments/return value:**

`element`: A list of the web elements.

`index`: Choose from the list of elements (default 0).

`return`: The value of the web element.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="is_checked"></a>is_checked


```python
is_checked(stype: SelectorType, sval: str, index: int = 0) -> str
```

*Create action `is_checked` checks if a web element is checked*

Returns true if a web element matching the selector stype with
the value sval is checked. An example where we check
an element with the name `"checkbox1"`:

```python
is_checked("name", "checkbox1")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default 0).

`return`: True if a web element (checkbox) matching the
selector `stype` with the value `sval` is checked.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_is_checked"></a>element_is_checked


```python
element_is_checked(element: splinter.element_list.ElementList, index: int = 0) -> bool
```

*Action `element_is_checked` checks if the web element is checked*

Check if the web element (checkbox) is checked.

**Arguments/return value:**

`element`: A list of the web elements.

`index`: Choose from the list of elements (default 0).

`return`: True if the web element (checkbox) is checked.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="is_not_present"></a>is_not_present


```python
is_not_present(stype: SelectorType, sval: str, wait_time: int | None = None) -> bool
```

*Action `is_not_present` checks if a web element is not present*

The action `is_not_present` checks if a web element based on
the selector type `stype` with the value `sval` is not
present. This example returns `True` if a web element with
name `"loginform"` is not present:

```python
is_not_present("name", "loginform")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`wait_time`: How long to wait for the web element to be
present (default `None`)

`return`: Returns True if the web element is not present.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="is_present"></a>is_present


```python
is_present(stype: SelectorType, sval: str, wait_time: int | None = None) -> bool
```

*Action `is_present` checks if a web element is present*

The action `is_present` checks if a web element based on a
selector type and the value of such a selector is present.
This example returns `True` if a web element with id `"news"`
is present:

```python
is_present("id", "news")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`wait_time`: How long to wait for the web element to be
present (default `None`).

`return`: Returns True if the web element is present.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="is_text_not_present"></a>is_text_not_present


```python
is_text_not_present(text: str, wait_time: int | None = None) -> bool
```

*Action `is_text_present` checks if a text is not present*

The action `is_text_not_present` checks if the text is not
present. This example returns `True` if the text `"Login
failed"` is not present:

```python
is_text_not_present("Login failed")
```

**Arguments/return value:**

`text`: The text that should't be present.

`wait_time`: How long to wait for the text to be present
(default `None`).

`return`: Returns `True` if the text is not present.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="is_text_present"></a>is_text_present


```python
is_text_present(text: str, wait_time: int | None = None) -> bool
```

*Action `is_text_present` checks if a text is present*

The action `is_text_present` checks if the text is
present. This example returns `True` if the text `"Login
succeeded"` is present within 3 seconds:

```python
is_text_present("Login succeeded", 3)
```

**Arguments/return value:**

`text`: The text to find.

`wait_time`: How long to wait for the text to be present
(default `None`).

`return`: Returns `True` if the text is present.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="scroll_to"></a>scroll_to


```python
scroll_to(stype: SelectorType, sval: str, index: int | None = None)
```

*Action `scroll_to` scrolls to a web element*

Scroll to a web element matching the selector `stype` with the
value `sval`. In this example, the view is scrolled to a `div`
element with a `class` attribute having the value
`"signature"`:

```python
scroll_to("xpath", "//div[@class='signature']")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default `None`).


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_scroll_to"></a>element_scroll_to


```python
element_scroll_to(element: splinter.element_list.ElementList, index: int | None = None)
```

*Action `element_scroll_to` scrolls to the web element*

Scroll to the web element.

**Arguments/return value:**

`element`: A list of the web elements.

`index`: Choose from the list of elements (default `None`).


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="select"></a>select


```python
select(val: str, stype: SelectorType, sval: str, index: int | None = None, doall: bool = False)
```

*Action `select` selects the value in a web element*

Select the given value `val` in a select web element matching
the selector `stype` with the value `sval`. In this example,
`"year"` is selected in the web element with the name
`"type"`:

```python
select("year", "name", "type")
```

**Arguments/return value:**

`val`: The value to fill in.

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_select"></a>element_select


```python
element_select(val: str, element: splinter.element_list.ElementList, index: int | None = None, doall: bool = False)
```

*Action `element_select` selects the value in the web element*

Select the given value `val` in the select web the element.

**Arguments/return value:**

`val`: The value to fill in.

`element`: A list of the web elements.

`index`: Choose from the list of elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="setvals"></a>setvals


```python
setvals(**kw)
```

*Action `setvals` sets values used later in the script*

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

**Arguments/return:**

`**kw`: Named arguments that set values in the namespace.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="uncheck"></a>uncheck


```python
uncheck(stype: SelectorType, sval: str, index: int | None = None, doall: bool = False)
```

*Action `uncheck` unchecks a web element (checkbox)*

Uncheck a checkbox web element matching the selector `stype`
with the value `sval`. This example unchecks a checkbox with
id `"include-comments"`:

```python
uncheck("id", "include-comments")
```

**Arguments/return value:**

`stype`: The selector type.

`sval`: The value of the selector type.

`index`: Choose from the list of matching elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="element_uncheck"></a>element_uncheck


```python
element_uncheck(element: splinter.element_list.ElementList, index: int | None = None, doall: bool = False)
```

*Action `element_uncheck` unchecks the web element (checkbox)*

Uncheck the checkbox web element.

**Arguments/return value:**

`element`:  A list of the web elements.

`index`: Choose from the list of elements (default `None`).

`doall`: If index is `None` and this is `True`, the action is
performed on all matching web elements.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="verify"></a>verify


```python
verify(val1: Any, val2: Any, errmsg: str = 'No match', assert_it: bool = True) -> bool | None
```

*Action `verify` checks that two values match*

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

**Arguments/return value:**

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


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="visit"></a>visit


```python
visit(url: str)
```

*Action `visit` is used to open a web page (URL)*

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

**Arguments/return value:**

`url`: The URL to be visited.


<!-- This documentation is generate using the `pypimdoc` module -->
<!-- Available from [PyPi](https://pypi.org/project/pypimdoc/)  -->


#### <a id="wait"></a>wait


```python
wait(wait_time: int = 1)
```

*Action `wait` waits for the given seconds in a script*

Used if you need to wait for web elements to be loaded or when
debugging scripts. Some other actions, like `is_present`, can
also wait for a while if the expected element is not present
yet (they have an optional argument `wait_time`).

**Arguments:**

`wait_time`: The amount of time to wait in seconds (default 1).







