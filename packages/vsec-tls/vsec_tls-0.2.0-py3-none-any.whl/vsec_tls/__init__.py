"""A precision-engineered TLS/HTTP client for replicating authentic browser fingerprints"""

# Velum Secure – Proprietary Software
# Copyright (c) Ferrum Legis Compliance. All rights reserved.
#
# This software is licensed, not sold. Unauthorized use, modification,
# redistribution, or reverse engineering is strictly prohibited.
#
# Use of this software requires a valid commercial license agreement with
# Ferrum Legis Compliance. For license terms, contact: info@ferrumlegis.com


'''
| |  | |   | |                 | |                               
| |  | |___| |_   _ ____        \ \   ____ ____ _   _  ____ ____ 
 \ \/ / _  ) | | | |    \        \ \ / _  ) ___) | | |/ ___) _  )
  \  ( (/ /| | |_| | | | |   _____) | (/ ( (___| |_| | |  ( (/ / 
   \/ \____)_|\____|_|_|_|  (______/ \____)____)\____|_|   \____)
'''


from .session import TlsSession
from .response import Response
from .exceptions import TlsClientError, ProfileError
from .profiles import get_profile, list_profiles, create_custom_profile

# Convenience function for quick requests
def create_session(**kwargs) -> TlsSession:
    """Create a new TLS session."""
    return TlsSession(**kwargs)

__all__ = [
    'TlsSession',
    'Response',
    'TlsClientError',
    'ProfileError',
    'create_session',
    'get_profile',
    'list_profiles',
    'create_custom_profile'
]