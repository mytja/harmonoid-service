import subprocess
import asyncio

import logging

logger = logging.getLogger(__name__)


COMMAND = 'youtube-dl --format "{format}" --no-progress --no-playlist --cookies {cookiefile} -x -o "{output}" "{url}"'
# TODO: use aria2c to increase speed


async def download(url, output, format="140", cookiefile="cookies.txt"):
    logger.info("[youtube-dl] Downloading video " + url)
    cmd = COMMAND.format(url=url, cookiefile=cookiefile, output=output, format=format)
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    while process.poll() is None:
        await asyncio.sleep(0.1)

    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    if process.poll() == 0:
        # success
        logger.info(stdout)
        return True
    else:
        # error
        logger.error(stderr)
        return False
