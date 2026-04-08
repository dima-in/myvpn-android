from __future__ import annotations

import subprocess
from datetime import datetime

import psutil


def get_xray_status() -> dict:
    result = subprocess.run(
        ["/bin/systemctl", "is-active", "xray"],
        capture_output=True,
        text=True,
    )
    return {
        "service": "xray",
        "active": result.stdout.strip() == "active",
        "raw": result.stdout.strip() or result.stderr.strip(),
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_system_metrics() -> dict:
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    disk = psutil.disk_usage("/")
    cpu = psutil.cpu_percent(interval=0.2)

    return {
        "cpu_percent": round(cpu, 1),
        "memory_total_mb": round(vm.total / 1024 / 1024, 1),
        "memory_used_mb": round(vm.used / 1024 / 1024, 1),
        "memory_available_mb": round(vm.available / 1024 / 1024, 1),
        "memory_percent": round(vm.percent, 1),
        "swap_total_mb": round(sm.total / 1024 / 1024, 1),
        "swap_used_mb": round(sm.used / 1024 / 1024, 1),
        "swap_percent": round(sm.percent, 1),
        "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
        "disk_used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
        "disk_percent": round(disk.percent, 1),
    }
