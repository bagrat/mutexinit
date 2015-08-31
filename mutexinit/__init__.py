from functools import wraps

__version__ = '0.0'

import inspect


class MutexInitMeta(type):
    ATTR_NAME_SUBINIT_MARK = '_issubinit'
    ATTR_NAME_ARGS = '_args'
    ATTR_NAME_ARG_MAP = '_arg_method_dict'

    def __new__(cls, name, bases, namespace):
        result = super(MutexInitMeta, cls).__new__(cls, name, bases, namespace)

        subinit_funcs = filter(
            lambda f: cls.is_subinit(f),
            map(
                lambda a: getattr(result, a),
                dir(result)
            )
        )
        arg_method_dict = {
            key: value for key, value in zip(
                map(
                    lambda f: getattr(f, cls.ATTR_NAME_ARGS),
                    subinit_funcs
                ),
                subinit_funcs
            )
        }
        setattr(result, cls.ATTR_NAME_ARG_MAP, arg_method_dict)

        def init_wrapper(self, **kwargs):
            provided_args = tuple(
                sorted(kwargs.keys())
            )

            sub_init = self._arg_method_dict.get(provided_args, None)

            if sub_init:
                sub_init(self, **kwargs)
            else:
                raise AttributeError('Insufficient arguments')

        result.__init__ = init_wrapper
        return result

    @classmethod
    def mark_subinit(cls, func, args):
        setattr(func, cls.ATTR_NAME_SUBINIT_MARK, True)
        setattr(func, cls.ATTR_NAME_ARGS, tuple(args))

    @classmethod
    def is_subinit(cls, f):
        return getattr(f, cls.ATTR_NAME_SUBINIT_MARK, False)


def subinit(func):
    exclude_args = ['self']
    args = [arg for arg in sorted(inspect.getargspec(func)[0]) if arg not in exclude_args]

    @wraps(func)
    def wrapper(funcself, **kwargs):
        if len(kwargs) == len(args):
            for arg in args:
                if (arg not in kwargs) or (kwargs[arg] is None):
                    raise AttributeError
        else:
            raise AttributeError

        return func(funcself, **kwargs)

    MutexInitMeta.mark_subinit(wrapper, args)

    return wrapper
