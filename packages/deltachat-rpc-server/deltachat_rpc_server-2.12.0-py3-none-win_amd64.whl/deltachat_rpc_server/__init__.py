import os, sys, subprocess
def main():
    argv = [os.path.join(os.path.dirname(__file__), "deltachat-rpc-server.exe"), *sys.argv[1:]]
    sys.exit(subprocess.call(argv))
