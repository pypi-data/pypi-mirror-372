######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.0                                                                                 #
# Generated on 2025-08-27T01:57:08.577969                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

