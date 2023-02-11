
"""
This module converts metadata into class instance.
"""

__version__ = '0.1'
__author__ = 'Aleksei Mashlakov'

import os
import sys

from typing import List, Optional, Dict
from pydantic import BaseModel

try:
    import logging
    from __main__ import logger_name
    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")

class ThingDescription(BaseModel):
    id: str
    #context: List[str]
    title: str
    discover: Dict
    #type: str
    #securityDefinitions: Optional[Dict] = {}
    #security: List
    #properties: Dict[Dict]
    #actions: Dict[Dict]
    #events: Dict[Dict]
