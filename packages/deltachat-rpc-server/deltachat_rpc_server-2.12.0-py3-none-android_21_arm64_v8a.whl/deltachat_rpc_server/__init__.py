import os, sys
def main():
    argv = [os.path.join(os.path.dirname(__file__), "deltachat-rpc-server"), *sys.argv[1:]]
    os.execv(argv[0], argv)
