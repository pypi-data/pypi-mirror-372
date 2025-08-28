# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

import inspect
from typing import TYPE_CHECKING

import grpc
import grpc.aio

if TYPE_CHECKING:
    from qctrlclient import ApiKeyAuth  # pyright: ignore[reportMissingImports]


class AuthInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
    grpc.aio.UnaryUnaryClientInterceptor,
    grpc.aio.UnaryStreamClientInterceptor,
    grpc.aio.StreamUnaryClientInterceptor,
    grpc.aio.StreamStreamClientInterceptor,
):
    def __init__(self, auth: "ApiKeyAuth"):
        self.auth = auth

    def _add_auth_metadata(self, client_call_details):
        token = self.auth.access_token

        # Add Authorization header to metadata
        metadata = client_call_details.metadata if client_call_details.metadata else []
        metadata = [*metadata, ("authorization", f"Bearer {token}")]

        return client_call_details._replace(metadata=metadata)

    async def _async_intercept(self, continuation, client_call_details, request):
        new_details = self._add_auth_metadata(client_call_details)
        return await continuation(new_details, request)

    def _sync_intercept(self, continuation, client_call_details, request):
        new_details = self._add_auth_metadata(client_call_details)
        return continuation(new_details, request)

    def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[override]
        if inspect.iscoroutinefunction(continuation):
            return self._async_intercept(continuation, client_call_details, request)
        return self._sync_intercept(continuation, client_call_details, request)

    async def intercept_unary_unary_async(
        self,
        continuation,
        client_call_details,
        request,
    ):
        return await self._async_intercept(continuation, client_call_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[override]
        if inspect.iscoroutinefunction(continuation):
            return self._async_intercept(continuation, client_call_details, request)
        return self._sync_intercept(continuation, client_call_details, request)

    async def intercept_unary_stream_async(
        self,
        continuation,
        client_call_details,
        request,
    ):
        return await self._async_intercept(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):  # type: ignore[override]
        if inspect.iscoroutinefunction(continuation):
            return self._async_intercept(continuation, client_call_details, request_iterator)
        return self._sync_intercept(continuation, client_call_details, request_iterator)

    async def intercept_stream_unary_async(
        self,
        continuation,
        client_call_details,
        request,
    ):
        return await self._async_intercept(continuation, client_call_details, request)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):  # type: ignore[override]
        if inspect.iscoroutinefunction(continuation):
            return self._async_intercept(continuation, client_call_details, request_iterator)
        return self._sync_intercept(continuation, client_call_details, request_iterator)

    async def intercept_stream_stream_async(
        self,
        continuation,
        client_call_details,
        request,
    ):
        return await self._async_intercept(continuation, client_call_details, request)
