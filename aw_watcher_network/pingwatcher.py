import subprocess
from subprocess import PIPE
from time import sleep
import logging
import re
import sys
from datetime import datetime
import pytz
from wireless import Wireless

from aw_core.models import Event
from aw_client import ActivityWatchClient

logger = logging.getLogger("aw-watcher-network")

# req_version is 3.5 due to usage of subprocess.run
# It would be nice to be able to use 3.4 as well since it's still common as of May 2016
req_version = (3,5)
cur_version = sys.version_info

if not cur_version >= req_version:
    logger.error("Your Python version is too old, 3.5 or higher is required.")
    exit(1)

# Starts pinging nbr times.
def ping(nbr) -> str:
    cmd = "ping -c " + str(nbr) +" 8.8.8.8"
    p = subprocess.Popen(cmd.split(), stdout=PIPE, universal_newlines = True)
    out = p.stdout.read()
    return " ".join(out.split("\n")[-3:-1])

# Parses data
def createEvents(out,timestamp,wifiname):
    spacesep = out.split(" ")
    maxping = 0
    meanping = 0
    minping = 0
    events = []
    total = int(spacesep[0])
    received = int(spacesep[3])
    failed = total - received

    if(spacesep[-1] == "ms"):
        extract = out.split("/")
        maxping = float(extract[-2])
        meanping = float(extract[-3])
        minping = float(extract[-4].split("= ")[-1])
        events.append(Event(timestamp=timestamp, label=["received","ssid:"+wifiname], count=received,
            duration=[{"value":meanping,"unit":"ms","label":meanping},
            {"value":maxping,"unit":"ms","label":maxping},{"value":minping,
            "unit":"ms","label":minping}]))
    events.append(Event(timestamp=timestamp, label=["failed", "ssid:"+wifiname], count=failed))

    return events

def main():
    import argparse

    parser = argparse.ArgumentParser("A watcher for ping")
    parser.add_argument("--testing", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.testing else logging.INFO)
    client = ActivityWatchClient("pingwatcher", testing=args.testing)

    bucketname = "{}_{}".format(client.client_name, client.client_hostname)
    eventtype = "ping"
    client.create_bucket(bucketname, eventtype)

    while True:
        t = datetime.utcnow()
        sleeptime = 60 - (t.second + t.microsecond/1000000.0)
        sleep(sleeptime)
        timestamp = datetime.now(pytz.utc)
        wifiname = Wireless().current()
        try:
            out = ping(30)
            client.send_events(bucketname, createEvents(out,timestamp,wifiname))
                
        except Exception as e:
            import sys, traceback
            traceback.print_exc()
            logger.error("Exception thrown while pinging {}".format(e))
        #sleep(1)

if __name__ == "__main__":
    main()
