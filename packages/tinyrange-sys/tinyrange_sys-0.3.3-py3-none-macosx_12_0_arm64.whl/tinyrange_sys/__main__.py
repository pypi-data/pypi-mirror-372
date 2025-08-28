import os, sys, subprocess
sys.exit(subprocess.call([
    os.path.join(os.path.dirname(__file__), "tinyrange"),
    *sys.argv[1:]
]))
