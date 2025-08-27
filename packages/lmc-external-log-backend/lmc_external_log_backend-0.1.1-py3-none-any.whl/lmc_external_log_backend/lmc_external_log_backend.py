import logging
from typing import List, Optional
from concurrent.futures import Future

# Third Party
import torch

# First Party
from lmcache.logging import init_logger
from lmcache.v1.storage_backend.abstract_backend import StorageBackendInterface
from lmcache.utils import CacheEngineKey
from lmcache.v1.memory_management import MemoryObj

logger = init_logger(__name__)


class ExternalLogBackend(StorageBackendInterface):
    def __init__(
        self,
        config,
        metadata,
        loop,
        memory_allocator,
        dst_device,
        lookup_server=None
    ):
        super().__init__(dst_device=dst_device)
        self.config = config
        self.metadata = metadata
        self.loop = loop
        self.memory_allocator = memory_allocator
        self.lookup_server = lookup_server
        logger.info(f"ExternalLogBackend initialized for device {dst_device}")

    def contains(self, key: CacheEngineKey, pin: bool = False) -> bool:
        logger.info(f"ExternalLogBackend Checking contains for key: {key}")
        return False

    def exists_in_put_tasks(self, key: CacheEngineKey) -> bool:
        logger.info(f"ExternalLogBackend Checking put tasks for key: {key}")
        return False

    def batched_submit_put_task(
        self,
        keys: List[CacheEngineKey],
        objs: List[MemoryObj],
        transfer_spec=None,
    ) -> Optional[List[Future]]:
        for key, obj in zip(keys, objs):
            logger.info(f"ExternalLogBackend Put task for key: {key}, size: {obj.tensor.size()}")
        return None

    def submit_prefetch_task(self, key: CacheEngineKey) -> bool:
        logger.info(f"ExternalLogBackend Prefetch task for key: {key}")
        return True

    def get_blocking(self, key: CacheEngineKey) -> Optional[MemoryObj]:
        logger.info(f"ExternalLogBackend Get blocking for key: {key}")
        return None

    def get_non_blocking(self, key: CacheEngineKey) -> Optional[Future]:
        logger.info(f"ExternalLogBackend Get non-blocking for key: {key}")
        return None

    def pin(self, key: CacheEngineKey) -> bool:
        logger.info(f"ExternalLogBackend Pin key: {key}")
        return True

    def unpin(self, key: CacheEngineKey) -> bool:
        logger.info(f"ExternalLogBackend Unpin key: {key}")
        return True

    def remove(self, key: CacheEngineKey, force: bool = True) -> bool:
        logger.info(f"ExternalLogBackend Remove key: {key}, force: {force}")
        return True

    def close(self) -> None:
        logger.info("ExternalLogBackend Closing ExternalLogBackend")
