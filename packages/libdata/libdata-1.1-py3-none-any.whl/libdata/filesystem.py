#!/usr/bin/env python3

__author__ = "xi"

from typing import Optional, Union

import fsspec
from fsspec import AbstractFileSystem

from libdata.common import LazyClient
from libdata.url import URL


class LazyFileSystem(LazyClient[AbstractFileSystem]):

    def __init__(self, url: Union[str, URL]):
        super().__init__()
        url = URL.ensure_url(url)

        schemes = url.split_scheme()
        self.fs_protocol = schemes[0]
        self.backend_protocol = schemes[-1]

        self.key = url.username
        self.secret = url.password
        self.endpoint = URL(scheme=self.backend_protocol, address=url.address).to_string()
        self.path = url.path.strip("/") if url.path else ""

    def _connect(self) -> AbstractFileSystem:
        return fsspec.filesystem(
            self.fs_protocol,
            key=self.key,
            secret=self.secret,
            client_kwargs={"endpoint_url": self.endpoint},
        )

    def _disconnect(self, client: AbstractFileSystem):
        if hasattr(client, "close"):
            client.close()
        elif hasattr(client, "disconnect"):
            client.disconnect()

    def _join_path(self, path: Optional[str]):
        if path:
            if path.startswith("/"):
                return path[1:]
            else:
                return self.path + path.lstrip("/")
        else:
            return self.path

    def ls(self, path: Optional[str] = None):
        path = self.path + path.lstrip("/") if path else self.path
        return self.client.ls(path)

    def open(
            self,
            path: str,
            mode="rb",
            block_size=None,
            cache_options=None,
            compression=None,
            **kwargs
    ):
        if not path.startswith(self.path):
            path = self.path + path.lstrip("/")
        return self.client.open(
            path=path,
            mode=mode,
            block_size=block_size,
            cache_options=cache_options,
            compression=compression,
            **kwargs
        )
