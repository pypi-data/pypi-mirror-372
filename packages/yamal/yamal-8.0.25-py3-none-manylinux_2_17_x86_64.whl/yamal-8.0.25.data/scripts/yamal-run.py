#!python

"""
    COPYRIGHT (c) 2024 by Featuremine Corporation.
    This software has been provided pursuant to a License Agreement
    containing restrictions on its use. This software contains valuable
    trade secrets and proprietary information of Featuremine Corporation
    and is protected by law. It may not be copied or distributed in any
    form or medium, disclosed to third parties, reverse engineered or used
    in any manner not provided for in said License Agreement except with
    the prior written authorization from Featuremine Corporation.
"""

from types import FrameType
from typing import Optional
from yamal import reactor, modules
import argparse
import signal
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Configuration path", required=True)
    parser.add_argument("--module", help="Module name", required=False, default=None)
    parser.add_argument("--component", help="Component name", required=False, default=None)
    parser.add_argument("--sched", help="Run reactor in scheduled mode", action='store_true')
    parser.add_argument("--affinity", help="Process CPU affinity", required=False, default=None, type=int)
    parser.add_argument("--priority", help="Process CPU priority", required=False, default=None, type=int)
    args = parser.parse_args()

    if (args.module is not None and args.component is None) or \
       (args.module is None and args.component is not None):
       raise RuntimeError("Invalid combination of arguments. module and component must either be provided through args or config.")

    r = reactor()

    component_mode = args.module is not None and args.component is not None
    deploy_mode = args.module is None and args.component is None
    assert not (component_mode and deploy_mode), "please specify both module and component to run, " + \
        "or use configuration to specify which components to run"

    config = json.load(open(args.config, 'r'))
    if component_mode:
        module = getattr(modules, args.module)
        component = getattr(module, args.component)
        comp = component(r, **config)
    else:
        r.deploy(config)

    def sighandle(sig: int, frm: Optional[FrameType]):
        r.stop()

    signal.signal(signal.SIGINT, sighandle)
    signal.signal(signal.SIGTERM, sighandle)

    r.run(live=not args.sched, affinity=args.affinity, priority=args.priority)

