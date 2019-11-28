#!/usr/bin/python2
#=======================================================================
import os
import sys
import threading
import Queue
import logging
log = logging.getLogger(__name__)
dbg = logging.getLogger('dbg.' + __name__)
#---------------------------------------
sys.path.insert(1, os.environ['PM_DIR'])
import tm
import util
#=======================================================================
class con(threading.Thread):
    def __init__(self,
                 group=None,
                 target=None,
                 name=None,
                 args=(),
                 kwargs=None,
                 verbose=None
                 ):
        threading.Thread.__init__(self,
                                  group=group,
                                  target=target,
                                  name=name,
                                  verbose=verbose
                                  )
        self.args = args
        self.kwargs = kwargs
        return

    def run(self):

#        dbg.info("running with %s and %s", self.args, self.kwargs)
        logging.debug("\nrunning with KWARG %s", self.kwargs)
        return
# END class remcon
con_data = {}
cond_data['host'] = util.get_host()

hosts = {'peart':'l', 'pi1':'r', 'pi2':'r', 'pi3':'r'}
for key in hosts.keys():
    t = remcon(kwargs={key:hosts[key]})
    t.start()
