###
# #%L
# aiSSEMBLE::Open Inference Protocol::FastAPI
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###

from fastapi import FastAPI

from aissemble_open_inference_protocol_shared.aissemble_oip_service import (
    AissembleOIPService,
)
from aissemble_open_inference_protocol_shared.handlers.dataplane import (
    DefaultHandler,
)

from aissemble_open_inference_protocol_shared.auth.default_adapter import (
    DefaultAdapter,
)
from aissemble_open_inference_protocol_fastapi.rest import endpoints
import uvicorn


class AissembleOIPFastAPI(AissembleOIPService):
    def __init__(self, handler=None, adapter=None):
        super().__init__(handler, adapter)
        self.server = FastAPI()
        self.server.include_router(endpoints.router)
        if self.handler is not None:
            self.server.dependency_overrides[DefaultHandler] = handler
        if self.adapter is not None:
            self.server.dependency_overrides[DefaultAdapter] = adapter

    async def start(self):
        config = uvicorn.Config(
            app=self.server,
            reload=self.config.fastapi_reload,
            host=self.config.fastapi_host,
            port=self.config.fastapi_port,
            use_colors=True,
        )
        server = uvicorn.Server(config=config)
        # Run FastAPI server
        await server.serve()

    def load(self):
        pass
