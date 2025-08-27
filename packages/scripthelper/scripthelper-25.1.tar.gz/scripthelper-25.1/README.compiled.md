# scripthelper

Helper module for simple command line Python scripts.


## Basic usage

[example1.py](https://github.com/presidento/scripthelper/blob/master/example1.py):

```python
#!/usr/bin/env python3
import scripthelper

logger = scripthelper.bootstrap()

logger.critical("critical message")
logger.error("error message")
logger.warning("warning message")
logger.info("info message")
logger.verbose("verbose message")
logger.debug("debug message")
logger.spam("spam message")
```

It just works. Try `--verbose` and `--quiet`  command line options, too.
It uses colored log messages on a terminal.
See `--help` for more information.

## Adding other command line parameters

[example2.py](https://github.com/presidento/scripthelper/blob/master/example2.py):

```python
#!/usr/bin/env python3
import scripthelper

scripthelper.add_argument("-n", "--name", help="Name to greet")
logger, args = scripthelper.bootstrap_args()

if args.name:
    logger.debug("Name was provided")
    logger.info(f"Hello {args.name}")
else:
    logger.warning("Name was not provided")
```

For bigger scripts it is good idea to have the logger at the very beginning, and encapsulate the argument parsing phase, which is typically in the main function:

[example2b.py](https://github.com/presidento/scripthelper/blob/master/example2b.py):

```python
#!/usr/bin/env python3
import scripthelper

logger = scripthelper.getLogger()


def greet(name):
    logger.info(f"Hello {name}")


def main():
    scripthelper.add_argument("--name", default="World")
    args = scripthelper.initialize()
    greet(args.name)


main()
```

## Progressbar works with logging, too

[example3.py](https://github.com/presidento/scripthelper/blob/master/example3.py):

```python
#!/usr/bin/env python3
import scripthelper
import time

logger = scripthelper.bootstrap()

logger.info("Doing the calculations...")
for i in scripthelper.progressbar(range(100)):
    if i % 20 == 0:
        logger.verbose(f"Iteration {i}")
    if i % 5 == 0:
        logger.debug(f"Iteration {i}")
    if logger.isEnabledFor(scripthelper.SPAM):
        logger.spam(f"Iteration {i}")
    time.sleep(0.01)
logger.info("Done")
```

It is automatically disabled on non-tty `stderr` by default.

## Extended log levels can be used in modules

[example4.py](https://github.com/presidento/scripthelper/blob/master/example4.py):

```python
#!/usr/bin/env python3
import scripthelper
import example4module

scripthelper.bootstrap()
example4module.do_the_things()
```

[example4module.py](https://github.com/presidento/scripthelper/blob/master/example4module.py):

```python
#!/usr/bin/env python3
import scripthelper

logger = scripthelper.getLogger(__name__)


def do_the_things():
    logger.verbose("Calling logger.verbose raises an exception if it does not work.")
    logger.info("Hello from a module.")
```

## You can easily preserve logs in files

[example5.py](https://github.com/presidento/scripthelper/blob/master/example5.py):

```python
#!/usr/bin/env python3
import scripthelper

logger = scripthelper.bootstrap()
scripthelper.setup_file_logging()

logger.critical("critical message")
logger.error("error message")
logger.warning("warning message")
logger.info("info message")
logger.verbose("verbose message")
logger.debug("debug message")
logger.spam("spam message")
```

## It handles exceptions, warnings

[example6.py](https://github.com/presidento/scripthelper/blob/master/example6.py):

```python
#!/usr/bin/env python3
import scripthelper

scripthelper.bootstrap()

scripthelper.warn("This user warning will be captured.")

this_variable = "will be displayed in stack trace"
as_well_as = "the other variables"
raise RuntimeError("This exception should be handled.")
```

The local variables will be displayed in stack trace, for example:

```
WARNING example6.py:6: UserWarning: This user warning will be captured.
  scripthelper.warn("This user warning will be captured.")

CRITICAL Uncaught RuntimeError: This exception should be handled.
File "example6.py", line 10, in <module>
    6    scripthelper.warn("This user warning will be captured.")
    7
    8    this_variable = "will be displayed in stack trace"
    9    as_well_as = "the other variables"
--> 10   raise RuntimeError("This exception should be handled.")
    ..................................................
     this_variable = 'will be displayed in stack trace'
     as_well_as = 'the other variables'
    ..................................................
```

## Has built-in colored pretty printer

[example7.py](https://github.com/presidento/scripthelper/blob/master/example7.py):

```python
#!/usr/bin/env python3
import scripthelper
from dataclasses import dataclass

scripthelper.bootstrap()


@dataclass
class Item:
    name: str
    value: int


something = {
    "string": "value1",
    "bool": True,
    "none": None,
    "integer": 1234,
    "item": Item("name", 999),
}

scripthelper.pp(something)
```

## Has built-in persisted state handler

The state is persisted immediately in the background in YAML. Mutable objects (`list`, `dict`) also can be used.

[example9.py](https://github.com/presidento/scripthelper/blob/master/example9.py):

```python
#!/usr/bin/env python3
import scripthelper

logger = scripthelper.bootstrap()
state = scripthelper.PersistedState(processed_id=0, to_remember=[])

state.processed_id += 1
state.to_remember.append(f"Element {state.processed_id}")
while len(state.to_remember) > 2:
    state.to_remember.pop(0)

logger.info(f"Processing item #{state.processed_id}")
for item in state.to_remember:
    logger.info(f"- {item}")
```

```
$ python3 example9.py
INFO example9 Processing item #1
INFO example9 - Element 1

$ python3 example9.py
INFO example9 Processing item #2
INFO example9 - Element 1
INFO example9 - Element 2

$ python3 example9.py
INFO example9 Processing item #3
INFO example9 - Element 2
INFO example9 - Element 3
```

## Helps issuing a warning only once

[example10.py](https://github.com/presidento/scripthelper/blob/master/example10.py):

```python
#!/usr/bin/env python3
import scripthelper

scripthelper.bootstrap()

for _ in range(10):
    scripthelper.warning_once("Item #12 has some errors")
```

