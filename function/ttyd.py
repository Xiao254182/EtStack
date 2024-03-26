import subprocess
from flask import redirect


def start_ttyd(ttyd_name):
    subprocess.call(['kill -9 $(ps -aux | grep -w "virsh" | awk \'{{print $2}}\')']
                    , shell=True)
    subprocess.Popen(["ttyd", "-W", "-t", "fontSize=25", "-a", "virsh", "console", ttyd_name])
