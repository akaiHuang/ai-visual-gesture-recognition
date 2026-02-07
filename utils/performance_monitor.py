"""
效能監控模組

即時監控 CPU、GPU、記憶體使用率，用於效能分析。
支援 macOS Metal GPU 監控。
"""

import psutil
import time
import platform
import subprocess
from typing import Dict, Optional
from dataclasses import dataclass


# 檢測作業系統
IS_MACOS = platform.system() == "Darwin"


@dataclass
class PerformanceMetrics:
    """效能指標數據類別"""
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    gpu_percent: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class PerformanceMonitor:
    """效能監控器
    
    監控 CPU、記憶體和 GPU（如果可用）的使用情況。
    """
    
    def __init__(self, process_id: Optional[int] = None):
        """初始化效能監控器
        
        Args:
            process_id: 要監控的進程 ID，None 表示當前進程
        """
        if process_id is None:
            self.process = psutil.Process()
        else:
            self.process = psutil.Process(process_id)
        
        # 檢查 GPU 可用性
        self.gpu_available = False
        self.gpu_type = None
        
        if IS_MACOS:
            # macOS: 使用 Metal GPU 監控
            try:
                # 測試是否能執行 powermetrics（需要 sudo）
                result = subprocess.run(
                    ["which", "powermetrics"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.gpu_available = True
                    self.gpu_type = "Metal"
                    print("✅ 偵測到 Metal GPU（使用 powermetrics）")
                    print("   注意：完整 GPU 數據需要 sudo 權限")
                else:
                    print("ℹ️  powermetrics 不可用，GPU 監控將受限")
            except Exception as e:
                print(f"⚠️  Metal GPU 監控初始化失敗: {e}")
        else:
            # 其他系統：嘗試使用 GPUtil
            try:
                import GPUtil
                self.GPUtil = GPUtil
                gpus = GPUtil.getGPUs()
                self.gpu_available = len(gpus) > 0
                if self.gpu_available:
                    self.gpu_type = "NVIDIA"
                    print(f"✅ 偵測到 {len(gpus)} 個 NVIDIA GPU")
            except ImportError:
                print("ℹ️  GPUtil 未安裝，GPU 監控將不可用")
                print("   安裝指令: pip install gputil")
            except Exception as e:
                print(f"⚠️  GPU 偵測失敗: {e}")
    
    def get_metrics(self) -> PerformanceMetrics:
        """獲取當前效能指標
        
        Returns:
            PerformanceMetrics 對象，包含所有效能數據
        """
        # CPU 使用率（當前進程）
        cpu_percent = self.process.cpu_percent(interval=0.1)
        
        # 記憶體使用
        mem_info = self.process.memory_info()
        memory_mb = mem_info.rss / (1024 * 1024)  # 轉換為 MB
        memory_percent = self.process.memory_percent()
        
        # GPU 使用率（如果可用）
        gpu_percent = None
        gpu_memory_mb = None
        
        if self.gpu_available:
            if IS_MACOS and self.gpu_type == "Metal":
                # macOS Metal GPU 監控
                # 注意：需要 sudo 權限，為避免反覆要求密碼，這裡不獲取數據
                # Metal 加速仍然運作，只是不顯示使用率
                gpu_percent = None
                    
            elif self.gpu_type == "NVIDIA":
                # NVIDIA GPU 監控
                try:
                    gpus = self.GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # 使用第一個 GPU
                        gpu_percent = gpu.load * 100
                        gpu_memory_mb = gpu.memoryUsed
                except Exception as e:
                    print(f"⚠️  GPU 讀取失敗: {e}")
        
        return PerformanceMetrics(
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            gpu_percent=gpu_percent,
            gpu_memory_mb=gpu_memory_mb
        )
    
    def get_system_info(self) -> Dict[str, str]:
        """獲取系統資訊
        
        Returns:
            包含系統資訊的字典
        """
        import platform
        
        info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': str(psutil.cpu_count(logical=True)),
            'cpu_physical_count': str(psutil.cpu_count(logical=False)),
            'total_memory_gb': f"{psutil.virtual_memory().total / (1024**3):.2f}",
        }
        
        if self.gpu_available:
            if IS_MACOS and self.gpu_type == "Metal":
                # macOS GPU 資訊
                try:
                    # 嘗試取得 GPU 名稱
                    result = subprocess.run(
                        ["system_profiler", "SPDisplaysDataType"],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        # 簡單解析 GPU 名稱
                        for line in result.stdout.split('\n'):
                            if 'Chipset Model' in line:
                                gpu_name = line.split(':')[1].strip()
                                info['gpu_name'] = gpu_name
                                break
                    info['gpu_type'] = 'Metal (Apple Silicon)'
                except:
                    info['gpu_type'] = 'Metal'
            elif self.gpu_type == "NVIDIA":
                try:
                    gpus = self.GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        info['gpu_name'] = gpu.name
                        info['gpu_memory_total_mb'] = f"{gpu.memoryTotal:.0f}"
                        info['gpu_type'] = 'NVIDIA'
                except:
                    pass
        
        return info
    
    def format_metrics(self, metrics: PerformanceMetrics) -> str:
        """格式化效能指標為可讀字串
        
        Args:
            metrics: 效能指標對象
            
        Returns:
            格式化的字串
        """
        lines = [
            f"CPU: {metrics.cpu_percent:.1f}%",
            f"記憶體: {metrics.memory_mb:.1f} MB ({metrics.memory_percent:.1f}%)",
        ]
        
        if metrics.gpu_percent is not None:
            lines.append(f"GPU: {metrics.gpu_percent:.1f}%")
        
        if metrics.gpu_memory_mb is not None:
            lines.append(f"GPU 記憶體: {metrics.gpu_memory_mb:.1f} MB")
        
        return " | ".join(lines)


class PerformanceTracker:
    """效能追蹤器
    
    持續追蹤效能指標，計算平均值、最大值等統計數據。
    """
    
    def __init__(self):
        """初始化效能追蹤器"""
        self.monitor = PerformanceMonitor()
        self.metrics_history = []
        self.start_time = time.time()
    
    def record(self):
        """記錄當前效能指標"""
        metrics = self.monitor.get_metrics()
        self.metrics_history.append(metrics)
    
    def get_statistics(self) -> Dict[str, float]:
        """計算統計數據
        
        Returns:
            包含平均值、最大值等的字典
        """
        if not self.metrics_history:
            return {}
        
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        mem_values = [m.memory_mb for m in self.metrics_history]
        
        stats = {
            'duration_seconds': time.time() - self.start_time,
            'samples': len(self.metrics_history),
            'cpu_avg': sum(cpu_values) / len(cpu_values),
            'cpu_max': max(cpu_values),
            'cpu_min': min(cpu_values),
            'memory_avg_mb': sum(mem_values) / len(mem_values),
            'memory_max_mb': max(mem_values),
            'memory_min_mb': min(mem_values),
        }
        
        # GPU 統計（如果有）
        gpu_values = [m.gpu_percent for m in self.metrics_history if m.gpu_percent is not None]
        if gpu_values:
            stats['gpu_avg'] = sum(gpu_values) / len(gpu_values)
            stats['gpu_max'] = max(gpu_values)
            stats['gpu_min'] = min(gpu_values)
        
        return stats
    
    def print_statistics(self):
        """列印統計數據"""
        stats = self.get_statistics()
        if not stats:
            print("尚無數據")
            return
        
        print("\n" + "="*60)
        print("效能統計")
        print("="*60)
        print(f"執行時間: {stats['duration_seconds']:.1f} 秒")
        print(f"採樣次數: {stats['samples']}")
        print(f"\nCPU 使用率:")
        print(f"  平均: {stats['cpu_avg']:.1f}%")
        print(f"  最大: {stats['cpu_max']:.1f}%")
        print(f"  最小: {stats['cpu_min']:.1f}%")
        print(f"\n記憶體使用:")
        print(f"  平均: {stats['memory_avg_mb']:.1f} MB")
        print(f"  最大: {stats['memory_max_mb']:.1f} MB")
        print(f"  最小: {stats['memory_min_mb']:.1f} MB")
        
        if 'gpu_avg' in stats:
            print(f"\nGPU 使用率:")
            print(f"  平均: {stats['gpu_avg']:.1f}%")
            print(f"  最大: {stats['gpu_max']:.1f}%")
            print(f"  最小: {stats['gpu_min']:.1f}%")
        
        print("="*60 + "\n")
    
    def reset(self):
        """重置追蹤器"""
        self.metrics_history.clear()
        self.start_time = time.time()


if __name__ == "__main__":
    # 簡單測試
    print("🧪 效能監控器測試\n")
    
    monitor = PerformanceMonitor()
    
    # 顯示系統資訊
    print("系統資訊:")
    info = monitor.get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n監控 5 秒...\n")
    
    # 監控 5 秒
    tracker = PerformanceTracker()
    for i in range(5):
        tracker.record()
        metrics = tracker.monitor.get_metrics()
        print(f"[{i+1}] {tracker.monitor.format_metrics(metrics)}")
        time.sleep(1)
    
    # 顯示統計
    tracker.print_statistics()
