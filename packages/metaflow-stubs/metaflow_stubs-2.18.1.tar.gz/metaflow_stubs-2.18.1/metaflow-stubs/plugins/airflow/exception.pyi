######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.1                                                                                 #
# Generated on 2025-08-29T13:35:56.201197                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from ...exception import MetaflowException as MetaflowException

class AirflowException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, msg):
        ...
    ...

class NotSupportedException(metaflow.exception.MetaflowException, metaclass=type):
    ...

