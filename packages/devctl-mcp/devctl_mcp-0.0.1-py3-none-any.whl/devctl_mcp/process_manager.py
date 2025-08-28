#!/usr/bin/env python3
"""
Process Manager for DevCtl MCP Server

Manages process lifecycle, logging, and cleanup for development processes.
"""

import asyncio
import logging
import os
import signal
import time
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import json

logger = logging.getLogger(__name__)


class ProcessInfo:
    """Information about a managed process."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.process: Optional[asyncio.subprocess.Process] = None
        self.start_time: Optional[float] = None
        self.log_buffer = deque(maxlen=1000)  # Keep last 1000 log lines
        self.status = "stopped"
        
    @property
    def pid(self) -> Optional[int]:
        return self.process.pid if self.process else None
    
    @property
    def is_running(self) -> bool:
        return self.process is not None and self.process.returncode is None


class ProcessManager:
    """Manages development processes with lifecycle and logging."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.processes: Dict[str, ProcessInfo] = {}
        self.config_path = config_path or "processes.yaml"
        self._shutdown = False
        
    async def initialize(self) -> None:
        """Initialize the process manager by loading config."""
        await self.load_config()
        
    async def load_config(self) -> None:
        """Load process definitions from config file."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.warning(f"Config file {self.config_path} not found. No processes defined.")
            return
            
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)
                    
            processes_config = data.get('processes', {})
            
            for name, config in processes_config.items():
                if not isinstance(config, dict) or 'cmd' not in config:
                    logger.error(f"Invalid config for process '{name}': missing 'cmd'")
                    continue
                    
                self.processes[name] = ProcessInfo(name, config)
                logger.info(f"Loaded process definition: {name}")
                
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            
    async def start_process(self, name: str) -> Tuple[bool, str]:
        """Start a named process."""
        if name not in self.processes:
            return False, f"Process '{name}' not found in config"
            
        process_info = self.processes[name]
        
        if process_info.is_running:
            return False, f"Process '{name}' is already running (PID: {process_info.pid})"
            
        config = process_info.config
        cmd = config['cmd']
        args = config.get('args', [])
        working_dir = config.get('working_directory')
        env = dict(os.environ)
        env.update(config.get('env', {}))
        
        try:
            # Start process in new process group for easier cleanup
            process = await asyncio.create_subprocess_exec(
                cmd, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=working_dir,
                env=env,
                preexec_fn=os.setsid  # Create new process group
            )
            
            process_info.process = process
            process_info.start_time = time.time()
            process_info.status = "running"
            
            # Start log capture task
            asyncio.create_task(self._capture_logs(process_info))
            
            logger.info(f"Started process '{name}' with PID {process.pid}")
            return True, f"Process '{name}' started successfully (PID: {process.pid})"
            
        except Exception as e:
            process_info.status = "failed"
            logger.error(f"Failed to start process '{name}': {e}")
            return False, f"Failed to start process '{name}': {str(e)}"
            
    async def stop_process(self, name: str, force: bool = False) -> Tuple[bool, str]:
        """Stop a named process."""
        if name not in self.processes:
            return False, f"Process '{name}' not found in config"
            
        process_info = self.processes[name]
        
        if not process_info.is_running:
            return False, f"Process '{name}' is not running"
            
        try:
            process = process_info.process
            
            if force:
                # Kill entire process group
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            else:
                # Graceful shutdown: SIGTERM to process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                
                # Wait up to 10 seconds for graceful shutdown
                try:
                    await asyncio.wait_for(process.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    # Force kill if graceful shutdown failed
                    logger.warning(f"Process '{name}' did not terminate gracefully, force killing")
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    
            # Clean up
            process_info.process = None
            process_info.status = "stopped"
            
            logger.info(f"Stopped process '{name}'")
            return True, f"Process '{name}' stopped successfully"
            
        except ProcessLookupError:
            # Process already dead
            process_info.process = None
            process_info.status = "stopped"
            return True, f"Process '{name}' was already stopped"
        except Exception as e:
            logger.error(f"Failed to stop process '{name}': {e}")
            return False, f"Failed to stop process '{name}': {str(e)}"
            
    async def get_process_logs(self, name: str, lines: Optional[int] = None) -> Tuple[bool, str, List[str]]:
        """Get logs for a named process."""
        if name not in self.processes:
            return False, f"Process '{name}' not found in config", []
            
        process_info = self.processes[name]
        log_lines = list(process_info.log_buffer)
        
        if lines is not None and lines > 0:
            log_lines = log_lines[-lines:]
            
        return True, f"Retrieved {len(log_lines)} log lines for '{name}'", log_lines
        
    def list_processes(self) -> List[Dict[str, Any]]:
        """List all processes and their status."""
        result = []
        for name, process_info in self.processes.items():
            uptime = None
            if process_info.start_time and process_info.is_running:
                uptime = time.time() - process_info.start_time
                
            result.append({
                'name': name,
                'status': process_info.status,
                'pid': process_info.pid,
                'uptime': uptime,
                'cmd': process_info.config['cmd'],
                'args': process_info.config.get('args', [])
            })
        return result
        
    async def shutdown(self) -> None:
        """Shutdown all processes gracefully."""
        logger.info("Shutting down process manager...")
        self._shutdown = True
        
        # Stop all running processes
        for name, process_info in self.processes.items():
            if process_info.is_running:
                logger.info(f"Stopping process '{name}' during shutdown")
                await self.stop_process(name, force=False)
                
    async def _capture_logs(self, process_info: ProcessInfo) -> None:
        """Capture stdout/stderr from a process."""
        try:
            while not self._shutdown and process_info.is_running:
                line = await process_info.process.stdout.readline()
                if not line:
                    break
                    
                log_line = line.decode('utf-8', errors='replace').rstrip()
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                formatted_line = f"[{timestamp}] {log_line}"
                
                process_info.log_buffer.append(formatted_line)
                
        except Exception as e:
            logger.error(f"Error capturing logs for {process_info.name}: {e}")
        finally:
            # Process ended
            if process_info.process:
                await process_info.process.wait()
                process_info.status = "stopped"
                logger.info(f"Process '{process_info.name}' terminated with code {process_info.process.returncode}")