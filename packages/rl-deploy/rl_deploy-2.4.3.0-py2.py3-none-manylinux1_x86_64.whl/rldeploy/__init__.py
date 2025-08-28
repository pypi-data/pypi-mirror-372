import os, sys, subprocess

def main():
    bin_path = os.path.join(os.path.dirname(__file__), "rl-deploy")
    sys.exit(subprocess.call([bin_path] + sys.argv[1:]))

