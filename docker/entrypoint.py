import os
import subprocess

REPO = "https://github.com/okeer/nst-tele-bot.git"
subprocess.run(["git", "clone", REPO])

os.system("mv nst-tele-bot/batch/* .")

import s3download
import run
import s3upload
