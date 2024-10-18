# unit test 
#
import sys, unittest

from utils import file_type


class testUtils(unittest.TestCase):
    def test_file_type(self):
        a = file_type('/a.html')
        self.assertEqual(a, 'text/html')
        a = file_type('/a.css')
        self.assertEqual(a, 'text/css')
        a = file_type('/a.js')
        self.assertEqual(a, 'application/javascript')
        a = file_type('/a.ico')
        self.assertEqual(a, 'image/vnd.microsoft.icon')
        a = file_type('/a.gif')
        self.assertEqual(a, 'image/gif')
        a = file_type('/a.bin')
        self.assertEqual(a, 'application/octet-stream')


from mpp_rest import baseRoute


class test_baseRoute(unittest.TestCase):
    def setUp(self) -> None:
        env = {
            "PATH_INFO": "/wsgi/environ",
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "http"}
        self.BR = baseRoute(env, self.callback)

    def callback(self, a, b):
        pass

    def test_methods(self):
        a = self.BR.do_DELETE()
        a = a[0].decode()
        self.assertIn('метод не поддерживается', a)


if __name__ == '__main__':
    argv = " ".join(sys.argv)
    if '-v' not in argv:  sys.argv += ["-v"]

    unittest.main()
