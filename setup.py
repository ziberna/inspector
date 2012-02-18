from distutils.core import setup

long_description = """
Inspector is a re-implementation of Andrew Moffat's Inspect-Shell.
 
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

You can also import the inspector from a Python shell if you just want to see
how it works.

See https://github.com/jzib/inspector for more information.
"""

setup(
    name='inspector',
    description='a Python server and shell for inspecting Python processes',
    long_description=long_description,
    author='Jure Ziberna and Andrew Moffat (Inspect-Shell)',
    author_email='j.ziberna@gmail.com',
    url='https://github.com/jzib/inspector',
    version='0.5.0',
    license='GNU GPL 3',
    py_modules=['inspector']
)
