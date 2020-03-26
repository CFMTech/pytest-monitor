import time

class TestClass:
    def setup_method(self, test_method):
        self.__value = test_method.__name__
        time.sleep(1)
       
    def test_method1(self):
        time.sleep(0.5)
        assert self.__value == "test_method1"
