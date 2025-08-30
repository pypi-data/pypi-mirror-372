import logging
import sys

import requests
import json
import importlib

import active.active as active

from volttron.platform.agent import utils
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub
from volttron.platform.scheduling import periodic
from volttron.platform.messaging.headers import TIMESTAMP
from volttron.platform.agent.utils import (get_aware_utc_now,
                                           format_timestamp)

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.3'

DEFAULT_HEARTBEAT_PERIOD = 30

class ACTIVEBootstrapAgent(Agent):
    '''
    Bootstrap VOLTTRON agent that loads an instance of ACTIVE within VOLTTRON and launches a VolttronAgent. 
    '''

    def __init__(self, config_path, **kwargs):
        super().__init__(**kwargs)
        self.config = utils.load_config(config_path)
        
        # Start ACTIVE and get the resultant Agent
        self.agent = active.execute("start", self.config, "Volttron")[0]

    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
        '''
        Provide VOLTTRON Interconnect Protocol handle to any requested objects, then schedule the agent's calls according to 
        the configuration file's defnintion.
        '''
        
        # For every item in the list, set VOLTTRON Agent's VIP to it
        for item in self.config["agents"][0]["parameters"]["set_vip"]:
            receiver = getattr(self.agent.strategy, item) 
            receiver.vip = self.vip
        
        # For each function in the schedule, set the function to run every period seconds
        for function, period in self.config["agents"][0]["parameters"]["schedule"].items():
            self.core.schedule(periodic(period), getattr(self.agent.strategy, function))


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(ACTIVEBootstrapAgent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
