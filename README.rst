mutexinit
=========

This package provides a *metaclass* and a *decorator* to enable mutually exclusive constructors for Python classes.

All you need to do is just make a class with the ``MutexInitMeta`` metaclass and declare each mutually exclusive constructor as a 
instance method, and also decorate it with ``@subinit`` decorator.

Here is a simple example::

    from mutexinit import MutexInitMeta, subinit
    
    class MyClass(object):
        __metaclass__ = MutexInitMeta

        @subinit
        def foo(self, bar, baz):
            print('Running "foo" constructor')
            
        @subinit
        def bar(self, foo, baz):
            print('Running "bar" constructor')
            
This is all to make a class to have mutually exclusive constructors. After defining the class, go ahead, and initialise it::
 
    >>> my_instance1 = MyClass(bar=1, baz=2)
    Running "foo" constructor
    >>> my_instance2 = MyClass(foo=9, baz=8)
    Running "bar" constructor
    >>> my_instance2 = MyClass(foo=None, baz=8)
    AttributeError: Mutex init arguments cannot be None
