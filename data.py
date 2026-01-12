import psutil
import GPUtil
import time
import platform
import subprocess


class System:
    def __init__(self):
        self.disk_path = 'C:\\'
        psutil.cpu_percent(interval=None)

        # Network Setup (for speed calculation)
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()

        # --- NEW: Fetch Static Hardware Specs Once ---
        self.specs = {
            "cpu": platform.processor(),  # Generic fallback
            "gpu": "Integrated Graphics",
            "ram": f"{round(psutil.virtual_memory().total / (1024 ** 3))} GB",
            "disk": "Local Disk (C:)"
        }

        # 1. Get Real CPU Name (Windows Command)
        try:
            command = "wmic cpu get name"
            output = subprocess.check_output(command, shell=True).decode().strip()
            # Clean up the output to get just the name line
            cpu_name = output.split('\n')[-1].strip()
            self.specs["cpu"] = cpu_name
        except:
            pass

        # 2. Get Real GPU Name
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                self.specs["gpu"] = gpus[0].name
        except:
            pass

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=None)

    def get_ram_usage(self):
        memory = psutil.virtual_memory()
        return {
            "percent": memory.percent,
            "used_gb": memory.used / (1024 ** 3),
            "total_gb": memory.total / (1024 ** 3)
        }

    def get_gpu_usage(self):
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    "name": gpu.name,
                    "load": gpu.load * 100,
                    "temp": gpu.temperature
                }
            return None
        except Exception:
            return None

    def get_disk_usage(self):
        disk = psutil.disk_usage(self.disk_path)
        return {
            "percent": disk.percent,
            "used_gb": disk.used / (1024 ** 3),
            "total_gb": disk.total / (1024 ** 3)
        }

    def get_top_processes(self):
        processes = []
        for p in psutil.process_iter(['name', 'memory_info']):
            try:
                mem_gb = p.info['memory_info'].rss / (1024 ** 3)
                processes.append((p.info['name'], mem_gb))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        top_5 = sorted(processes, key=lambda x: x[1], reverse=True)[:5]
        return top_5

    def get_network_speed(self):
        current_net = psutil.net_io_counters()
        current_time = time.time()

        time_diff = current_time - self.last_time
        if time_diff == 0: time_diff = 1

        bytes_sent = current_net.bytes_sent - self.last_net.bytes_sent
        bytes_recv = current_net.bytes_recv - self.last_net.bytes_recv

        sent_kbs = (bytes_sent / 1024) / time_diff
        recv_kbs = (bytes_recv / 1024) / time_diff

        self.last_net = current_net
        self.last_time = current_time

        return {"upload": sent_kbs, "download": recv_kbs}