"""
Docker Health Manager - Ensures Docker daemon stays healthy during evaluations
"""

import subprocess
import time
import logging
import platform
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class DockerHealthManager:
    """Manages Docker daemon health and recovery."""
    
    def __init__(self):
        self.system = platform.system()
        self.last_check_time = 0
        self.check_interval = 30  # Check every 30 seconds
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        
    def check_docker_health(self) -> bool:
        """Check if Docker daemon is healthy."""
        try:
            result = subprocess.run(
                ['docker', 'version', '--format', '{{.Server.Version}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def restart_docker_daemon(self) -> bool:
        """Attempt to restart Docker daemon based on platform."""
        logger.warning("⚠ Attempting to restart Docker daemon...")
        
        try:
            if self.system == "Darwin":  # macOS
                # Try Docker Desktop restart
                subprocess.run(['osascript', '-e', 'quit app "Docker"'], 
                             capture_output=True, timeout=10)
                time.sleep(3)
                subprocess.run(['open', '-a', 'Docker'], 
                             capture_output=True, timeout=10)
                
                # Wait for Docker to start up
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    if self.check_docker_health():
                        logger.info("✅ Docker daemon restarted successfully")
                        return True
                        
            elif self.system == "Linux":
                # Try systemctl first (systemd)
                result = subprocess.run(['sudo', 'systemctl', 'restart', 'docker'],
                                      capture_output=True, timeout=30)
                if result.returncode == 0:
                    time.sleep(5)
                    if self.check_docker_health():
                        logger.info("✅ Docker daemon restarted successfully")
                        return True
                
                # Try service command (init.d)
                result = subprocess.run(['sudo', 'service', 'docker', 'restart'],
                                      capture_output=True, timeout=30)
                if result.returncode == 0:
                    time.sleep(5)
                    if self.check_docker_health():
                        logger.info("✅ Docker daemon restarted successfully")
                        return True
                        
            elif self.system == "Windows":
                # Try restarting Docker Desktop service
                subprocess.run(['powershell', 'Restart-Service', 'docker'],
                             capture_output=True, timeout=30)
                time.sleep(10)
                if self.check_docker_health():
                    logger.info("✅ Docker daemon restarted successfully")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Failed to restart Docker daemon: {e}")
            
        return False
    
    def ensure_docker_healthy(self, force_check: bool = False) -> bool:
        """
        Ensure Docker is healthy, attempt recovery if not.
        
        Args:
            force_check: Force a health check regardless of interval
            
        Returns:
            True if Docker is healthy or recovered, False otherwise
        """
        current_time = time.time()
        
        # Check if we should perform a health check
        if not force_check and (current_time - self.last_check_time) < self.check_interval:
            return True  # Assume healthy if recently checked
            
        self.last_check_time = current_time
        
        # Check Docker health
        if self.check_docker_health():
            self.recovery_attempts = 0  # Reset counter on success
            return True
            
        # Docker is not healthy, attempt recovery
        logger.error("❌ Docker daemon is not responding")
        
        if self.recovery_attempts >= self.max_recovery_attempts:
            logger.error(f"❌ Max recovery attempts ({self.max_recovery_attempts}) reached")
            return False
            
        self.recovery_attempts += 1
        logger.info(f"🔧 Recovery attempt {self.recovery_attempts}/{self.max_recovery_attempts}")
        
        # Attempt to restart Docker
        if self.restart_docker_daemon():
            self.recovery_attempts = 0  # Reset on successful recovery
            return True
            
        return False
    
    def cleanup_docker_resources(self) -> None:
        """Clean up Docker resources to free memory and prevent daemon issues."""
        try:
            # Remove stopped containers
            subprocess.run(['docker', 'container', 'prune', '-f'],
                         capture_output=True, timeout=30)
            
            # Remove unused images (keep tagged ones)
            subprocess.run(['docker', 'image', 'prune', '-f'],
                         capture_output=True, timeout=30)
            
            # Remove unused volumes
            subprocess.run(['docker', 'volume', 'prune', '-f'],
                         capture_output=True, timeout=30)
            
            # Remove unused networks
            subprocess.run(['docker', 'network', 'prune', '-f'],
                         capture_output=True, timeout=30)
            
            logger.debug("✓ Docker resources cleaned up")
            
        except Exception as e:
            logger.warning(f"⚠ Failed to clean Docker resources: {e}")
    
    def get_docker_info(self) -> Optional[dict]:
        """Get Docker system information."""
        try:
            result = subprocess.run(['docker', 'system', 'info', '--format', '{{json .}}'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except Exception:
            pass
        return None
    
    def check_docker_resources(self) -> Tuple[bool, str]:
        """
        Check if Docker has sufficient resources.
        
        Returns:
            Tuple of (has_sufficient_resources, message)
        """
        info = self.get_docker_info()
        if not info:
            return False, "Cannot get Docker info"
            
        # Check available disk space
        if 'DriverStatus' in info:
            for item in info['DriverStatus']:
                if len(item) >= 2 and 'Data Space Available' in item[0]:
                    # Parse space (e.g., "10.5GB")
                    space_str = item[1]
                    try:
                        if 'GB' in space_str:
                            space_gb = float(space_str.replace('GB', ''))
                            if space_gb < 5:
                                return False, f"Low disk space: {space_gb:.1f}GB available"
                        elif 'MB' in space_str:
                            space_mb = float(space_str.replace('MB', ''))
                            if space_mb < 5000:
                                return False, f"Low disk space: {space_mb:.0f}MB available"
                    except:
                        pass
                        
        # Check memory
        if 'MemTotal' in info:
            mem_bytes = info['MemTotal']
            mem_gb = mem_bytes / (1024 ** 3)
            if mem_gb < 2:
                return False, f"Low memory: {mem_gb:.1f}GB available"
                
        return True, "Resources OK"


# Global instance for use across the harness
docker_health_manager = DockerHealthManager()