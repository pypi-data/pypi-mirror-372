###
# #%L
# aiSSEMBLE::Open Inference Protocol::Shared
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from abc import ABC, abstractmethod
from typing import Optional, Type, Union

from aissemble_open_inference_protocol_shared.auth.auth_adapter_base import (
    AuthAdapterBase,
)
from aissemble_open_inference_protocol_shared.config.oip_config import OIPConfig
from aissemble_open_inference_protocol_shared.handlers.dataplane import (
    DataplaneHandler,
)


class AissembleOIPService(ABC):
    """
    Abstract class for all aiSSEMBLE Open Inference Protocol solutions. Defines required standardization.
    """

    def __init__(
        self,
        handler: Union[DataplaneHandler, Type[DataplaneHandler]],
        adapter: Optional[Union[AuthAdapterBase, Type[AuthAdapterBase]]],
    ):
        super(AissembleOIPService, self).__init__()
        self.config = OIPConfig()
        self.handler = handler
        self.adapter = adapter
        self.server = None

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    async def start(self):
        pass
