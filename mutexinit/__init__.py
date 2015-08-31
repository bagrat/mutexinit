from functools import wraps

__version__ = '0.0'

import inspect


class MutexInitMeta(type):
    ATTR_NAME_SUBINIT_MARK = '_issubinit'
    ATTR_NAME_ARGS = '_args'
    ATTR_NAME_ARG_MAP = '_arg_method_dict'

    def __new__(mcs, name, bases, namespace):
        # Initialise the class
        klass = super(MutexInitMeta, mcs).__new__(mcs, name, bases, namespace)

        # Get all methods marked as subinit
        subinit_funcs = filter(
            lambda f: mcs.is_subinit(f),
            map(
                lambda a: getattr(klass, a),
                dir(klass)
            )
        )
        # Generate and store the argument-method mapping dictionary
        arg_method_dict = {
            key: value for key, value in zip(
                map(
                    lambda f: getattr(f, mcs.ATTR_NAME_ARGS),
                    subinit_funcs
                ),
                subinit_funcs
            )
        }
        setattr(klass, mcs.ATTR_NAME_ARG_MAP, arg_method_dict)

        # Define __init__ wrapper, that validates and dispatches to subinit
        def init_wrapper(self, **kwargs):
            provided_args = tuple(
                sorted(kwargs.keys())
            )

            sub_init = self._arg_method_dict.get(provided_args, None)
            if not sub_init:
                raise AttributeError('Insufficient arguments')

            sub_init(self, **kwargs)

        # Replace __init__ with the wrapper
        klass.__init__ = init_wrapper
        return klass

    @classmethod
    def mark_subinit(mcs, func, args):
        setattr(func, mcs.ATTR_NAME_SUBINIT_MARK, True)
        setattr(func, mcs.ATTR_NAME_ARGS, tuple(args))

    @classmethod
    def is_subinit(mcs, func):
        return getattr(func, mcs.ATTR_NAME_SUBINIT_MARK, False)


def subinit(func):
    # Filter out the arguments of method being wrapped
    exclude_args = ['self']
    args = [arg for arg in sorted(inspect.getargspec(func)[0]) if arg not in exclude_args]

    @wraps(func)
    def wrapper(funcself, **kwargs):
        # Check if any supplied argument is None
        if [arg for arg in args if kwargs.get(arg) is None]:
            raise AttributeError('Mutex init arguments cannot be None')

        return func(funcself, **kwargs)

    # Mark the method as subinit (note the wrapper is marked)
    MutexInitMeta.mark_subinit(wrapper, args)

    return wrapper
