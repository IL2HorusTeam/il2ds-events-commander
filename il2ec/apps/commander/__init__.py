# -*- coding: utf-8 -*-
"""
Django application of IL-2 Dedicated Server events commander.
"""

def stop_everything_n_quit():
    """
    Stop the whole commander and quit.
    """
    from twisted.internet import reactor
    if reactor.running:
        reactor.stop()
