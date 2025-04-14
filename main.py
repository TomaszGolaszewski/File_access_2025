# import read_file_lib as mylib
from read_file_lib.file_handling import FileWithConstantWidth
# from read_file_lib import * 

def run_demo():
    file = FileWithConstantWidth("c.txt")

if __name__ == '__main__':
    run_demo()
    # print(type(123456789012).__name__)