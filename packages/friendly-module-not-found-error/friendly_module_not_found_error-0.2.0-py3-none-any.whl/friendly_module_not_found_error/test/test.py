import traceback
import unittest
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

class ExceptionTest(unittest.TestCase):
    def test_top_import_exception(self):
        import_error_tuple = (
            ("import ant", ModuleNotFoundError, "No module named 'ant'. Did you mean: 'ast'?"),
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def test_non_packages_import_exception(self):
        import_error_tuple = (
            ("import os.path.a", ModuleNotFoundError,
             "module 'os.path' has no child module 'a'; 'os.path' is not a package"),
            ("import ast.a", ModuleNotFoundError, "module 'ast' has no child module 'a'; 'ast' is not a package")
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def test_packages_import_exception(self):
        import_error_tuple = (
            ("import multiprocessing.dumy", ModuleNotFoundError,
             "module 'multiprocessing' has no child module 'dumy'. Did you mean: 'dummy'?"),
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def test_wrong_module_exception(self):
        import_error_tuple = (
            ("import wrong_module", ModuleNotFoundError,
             "module 'wrong_module' has no child module 'wrong_module'"),
            ("import wrong_child_module.wrong_child_module", ModuleNotFoundError,
             "module 'wrong_child_module.wrong_child_module' has no child module 'wrong_child_module'. Did you mean: 'wrong_child_modules'?")
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def check_message(self, code, exc_type, exc_msg):
        try:
            exec(code)
        except exc_type:
            self.assertIn(exc_msg, traceback.format_exc())


main = unittest.main

if __name__ == '__main__':
    main()
