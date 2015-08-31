from unittest import TestCase
from mock import MagicMock
from mutexinit import MutexInitMeta, subinit


class MainTests(TestCase):
    def test_main(self):
        init1_call = MagicMock()
        init2_call = MagicMock()

        class SomeClass(object):
            __metaclass__ = MutexInitMeta

            @subinit
            def init1(self, param1, param2):
                init1_call()

            @subinit
            def init2(self, param2, param3):
                init2_call()

        obj = SomeClass(param1=0, param2=0)
        init1_call.assert_called_once_with()
        init2_call.assert_not_called()

        obj = SomeClass(param2=0, param3=0)
        init1_call.assert_called_once_with()  # This is the previous call
        init2_call.assert_called_once_with()

        self.assertRaises(AttributeError, SomeClass, blablabla=0)
        init1_call.assert_called_once_with()  # This is the previous call again
        init2_call.assert_called_once_with()  # This is the previous call
