import time
import os


class MyTest():
    def __init__(self, id):
        self.id = id
        self.name = self.__class__.__name__

    def get_id(self,):
        return self.id

    def work(self, t):
        start_time = time.time()
        s1 = f'{self.id} starts working for {t}s at t={start_time}. '
        # print (s1)
        while time.time() < start_time + t:
            pass
        s2 = f'{self.id} ends working at {time.time()}.'
        # print (s2)
        return s1 + s2

    def return_input(self, *args, **kwargs):
        return f"{self.id} got: {str(args)} and {str(kwargs)}"

    def get_ld_library_path(self):
        return os.environ['LD_LIBRARY_PATH']

    def close(self):
        return f"closing {self.get_id()}"

    def raise_exception(self):
        1 / 0  # raise ZeroDivisionError
