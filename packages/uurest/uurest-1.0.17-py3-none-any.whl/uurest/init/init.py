import os


def init():
    print(f"\n\nPreparing directory\n\n{os.getcwd()}\n{os.path.realpath(__file__)}\n\n")


init()
