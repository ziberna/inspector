_Inspector_ is a re-implementation of Andrew Moffat's
[Inspect-Shell](https://github.com/amoffat/Inspect-Shell).

It works with Python 2 and 3.


What it does
------------

Inspector allows you to read, change or add global variables of your Python
program from another process (a shell) while your program is running.

You could, for example, add a whole class to your program from the shell and
rewrite some function so that it starts using your newly-created class. All that
while your program continues to run! Yes, that's pretty cool.


How it works
------------

Inspector has 2 modes; server mode and shell mode. Server mode is run by your
Python program (in a separate thread), while the shell mode is run by the
inspector itself.

Steps:

 1. add `import inspector` to your program
 2. run your program
 3. run the inspector with `python inspector.py`
 4. type code into the shell

Inspector also supports tab completion for your program's variables.

After you're done, exit the shell by pressing Ctrl-D or Ctrl-C, or typing
`exit`. You program will continue to run with all the changes made. You can run
the inspector again anytime you want.

You can also import the inspector from a Python shell if you just want to see
how it works.


Example
-------

### Importer's side (your program)

```python
import inspector  # add this line to your program
import time

a = 1
b = 10
limit = 600
update = lambda n: n + 1

while a <= limit:
    if a % b == 0:
        print(a, b)
    a = update(a)
    time.sleep(1)
```


### Inspector's side (the shell) 

    [user@host dir]$ python inspector.py
    <Inspector @ localhost:2971 (importer_file_name.py)>
    >>> a
    9
    >>> a = 100
    >>> a
    102
    >>> b = 1
    >>> def update(n):
    ...     if n % 2 == 0:
    ...         n = n // 2
    ...     else:
    ...         n = n * 3 + 1
    ...     return n
    ...
    >>> a = 1000 


Advanced options
----------------

Inspector allows you to change various settings by adding a variable to your
program before importing the inspector:

```python
INSPECTOR_VARIABLE_NAME = 'some value'
import inspector

# and your program here
```

Possible settings are:

 - INSPECTOR\_HOST = _your-host-name_
 - INSPECTOR\_PORT = _port-number_
 - INSPECTOR\_TIMEOUT = _seconds_
 - INSPECTOR\_PASSPHRASE = 'anything you want'

If you set these, you'll have to tell the inspector's shell about them, so
it can connect properly to your program. You do this by adding command-line
arguments, like so:

    [user@host dir]$ python inspector.py -l <host> -p <port> -t <timeout> -s <passphrase>

Run `python inspector.py --help` to get a help message about command-line arguments.


There are two other options that I haven't mentioned yet. These are:

 - INSPECTOR\_SHELL = True
 - INSPECTOR\_DISABLE = True

The first one enables shell mode instead of server mode. The second one turns
inspector into a normal module, so that you can use parts of it without running
the server in the background.


Authors
-------

__Andrew Moffat__, author of the official (original) implementation and the idea
itself  
__Jure Žiberna__, author of this re-implementation
