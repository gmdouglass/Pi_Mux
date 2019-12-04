#!/usr/bin/python3
#=======================================================================
"""
import os
import re
import shlex
import subprocess
import sys
import tempfile
"""
import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%s(threadName)-10s) \n%(message)s',
                    )

#log = logging.getLogger(__name__)
#dbg = logging.getLogger('dbg.' + __name__)
#=======================================================================
class remcon(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target,
                                  name=name, verbose=verbose
                                  )
        self.args = args
        self.kwargs = kwargs
        return

    def run(self):
#        dbg.info("running with %s and %s", self.args, self.kwargs)
        logging.debug("\nrunning with KWARG %s", self.kwargs)
        return
# END class remcon

hosts = {'peart':'l', 'pi1':'r', 'pi2':'r', 'pi3':'r'}
for key in hosts.keys():
    t = remcon(kwargs={key:hosts[key]})
    t.start()
