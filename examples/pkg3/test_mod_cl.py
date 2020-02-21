class TestClass:
    def setup_method(self, test_method):
        self.__value = test_method.__name__
       
    def test_method1(self):
        assert self.__value == "test_method1"
