_Inspector_ is a re-implementation of Andrew Moffat's
[Inspect-Shell](https://github.com/amoffat/Inspect-Shell). At the moment it
doesn't support saving shell history to a file or auto-completion. The
additional features are:

 - setting host, timeout and message passphrase. Port can also be set, but this
   can already be done in the official implementation.
 - server side notifications about client connections

It runs in both Python 2 and 3. Since the server (inspector importer) and the
client (inspector shell) are both separate processes, you can even run one side
in Python 3 and the other in Python 2. Everything you type into the shell will
be evaluated with server's Python version though.

--------------------------------------------------------------------------------


Example
-------


### Importer's side

The file that imports inspector will run a server. Importing the inspector
is enough.

```python
import time
import inspector

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

You can also import the inspector from a Python shell if you want to just test
how it works.


### Inspector's side

Run the inspector shell with `python inspector.py`. I advise  you to create a
symlink to the inspector.py somewhere on your `$PATH`, so that you can run it
from anywhere.

    <Inspector @ localhost:2971 (importer_file_name.py)>
    >>> a
    9
    >>> a = 100
    >>> a
    102
    >>> b = 2
    >>> update = lambda n: n * 2
    >>> a = 1
    >>> limit = 4096

--------------------------------------------------------------------------------


Authors
-------

__Andrew Moffat__, author of the official (original) implementation and the idea
itself  
__Jure Žiberna__, author of this re-implementation
