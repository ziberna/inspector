_Inspector_ is a re-implementation of Andrew Moffat's
[Inspect-Shell](https://github.com/amoffat/Inspect-Shell). It doesn't support
autocompletion yet.

It runs with both Python 2 and 3. Since the server (inspector importer) and the
client (inspector shell) are separate processes, you can even run one side
in Python 3 and the other in Python 2. Everything you type into the shell will
be evaluated from both sides though.


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

After you're done, exit the shell by pressing Ctrl-D or Ctrl-C, or typing
`exit`. You program will continue to run with all the changes made. You can run
the inspector again anytime you want.


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

You can also import the inspector from a Python shell if you just want to see
how it works.


### Inspector's side (the shell)

Run the inspector shell with `python inspector.py`. 

    [jure@Kant inspector]$ python inspector.py
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

Create a symlink to the inspector.py somewhere on your `$PATH`, so that you can
run it from anywhere.


Options
-------

 - `inspector.VERBOSE` level of status updates
 - `inspector.HOST`
 - `inspector.PORT`
 - `inspector.TIMEOUT_SERVER`
 - `inspector.TIMEOUT_CLIENT`
 - `inspector.PASSPHRASE` to ensure nobody is messing with your variables' values
 - `inspector.CHUNK_SIZE` of each message chunk that is recieved


Command-line arguments
----------------------

    usage: inspector.py [-h] [-l host] [-p port] [-t timeout] [-s passphrase]
    
    Inspector
    
    optional arguments:
      -h, --help     show this help message and exit
      -l host
      -p port
      -t timeout
      -s passphrase


Authors
-------

__Andrew Moffat__, author of the official (original) implementation and the idea
itself  
__Jure Žiberna__, author of this re-implementation
