"""Core system inspection utilities."""
from __future__ import annotations

import asyncio
import platform
import socket
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Callable, AsyncIterator, List

import psutil


@dataclass
class SystemSnapshot:
    timestamp: float
    cpu_percent: float
    cpu_count: int
    mem_total: int
    mem_used: int
    mem_percent: float
    swap_total: int
    swap_used: int
    disk: Dict[str, Any]
    network: Dict[str, Any]
    boot_time: float
    platform: str


class SystemInspector:
    """High-level API to gather system information and provide async monitoring streams.

    This class intentionally avoids executing arbitrary shell commands to remain safe.
    """

    def __init__(self, poll_interval: float = 1.0):
        self.poll_interval = poll_interval

    def snapshot(self) -> SystemSnapshot:
        ts = time.time()
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = psutil.cpu_count(logical=True) or 1
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = {p.mountpoint: psutil.disk_usage(p.mountpoint)._asdict() for p in psutil.disk_partitions(all=False)}
        net_io = psutil.net_io_counters(pernic=True)
        network = {k: v._asdict() for k, v in net_io.items()}
        boot_time = psutil.boot_time()
        plat = f"{platform.system()} {platform.release()}"
        return SystemSnapshot(
            timestamp=ts,
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            mem_total=vm.total,
            mem_used=vm.used,
            mem_percent=vm.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            disk=disk,
            network=network,
            boot_time=boot_time,
            platform=plat,
        )

    async def stream(self) -> AsyncIterator[Dict[str, Any]]:
        """Async generator that yields snapshots every poll_interval seconds."""
        while True:
            snap = self.snapshot()
            yield asdict(snap)
            await asyncio.sleep(self.poll_interval)

    def simple_report(self) -> Dict[str, Any]:
        """Return a small human-friendly report dict."""
        s = self.snapshot()
        return {
            "time": s.timestamp,
            "platform": s.platform,
            "cpu": {
                "percent": s.cpu_percent,
                "count": s.cpu_count,
            },
            "memory": {
                "used": s.mem_used,
                "total": s.mem_total,
                "percent": s.mem_percent,
            },
        }
