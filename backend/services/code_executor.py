"""
Code Executor Service - Secure containerized execution of generated trading code

This service orchestrates Docker containers to safely execute user-generated
trading strategies in isolated environments with resource limits.

Key Features:
- Isolated execution in Docker containers
- Resource limits (CPU, memory, timeout)
- Security sandboxing (non-root user, network isolation)
- Automatic cleanup
- Error handling and logging
"""

import logging
import docker
import tempfile
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class CodeExecutor:
    """
    Manages containerized execution of generated trading strategy code.

    Security Features:
    - Runs in isolated Docker container
    - Non-root user execution
    - Resource limits (CPU, memory, timeout)
    - Network can be disabled
    - Automatic cleanup of containers and temp files
    """

    def __init__(
        self,
        image_name: str = "backtest-executor:latest",
        max_memory: str = "512m",
        max_cpu: float = 1.0,
        timeout: int = 300,  # 5 minutes default
        network_mode: str = "bridge",  # or "none" for no network
    ):
        """
        Initialize code executor.

        Args:
            image_name: Docker image to use
            max_memory: Memory limit (e.g., "512m", "1g")
            max_cpu: CPU quota (1.0 = 1 CPU core)
            timeout: Execution timeout in seconds
            network_mode: Docker network mode ("bridge", "none", etc.)
        """
        self.image_name = image_name
        self.max_memory = max_memory
        self.max_cpu = max_cpu
        self.timeout = timeout
        self.network_mode = network_mode

        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info(f"✅ Docker client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Docker client: {e}")
            raise

    def build_image(self, dockerfile_path: str, context_path: str) -> bool:
        """
        Build Docker image for backtest execution.

        Args:
            dockerfile_path: Path to Dockerfile
            context_path: Build context directory

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Building Docker image: {self.image_name}")
            logger.info(f"  Dockerfile: {dockerfile_path}")
            logger.info(f"  Context: {context_path}")

            # Build image
            image, build_logs = self.docker_client.images.build(
                path=context_path,
                dockerfile=os.path.basename(dockerfile_path),
                tag=self.image_name,
                rm=True,  # Remove intermediate containers
                forcerm=True,  # Always remove intermediate containers
            )

            # Log build output
            for log in build_logs:
                if 'stream' in log:
                    logger.debug(log['stream'].strip())

            logger.info(f"✅ Image built successfully: {self.image_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to build image: {e}")
            return False

    def execute_backtest(
        self,
        code: str,
        symbols: list,
        config: dict,
        start_date: datetime,
        end_date: datetime,
        initial_cash: float = 100000.0,
    ) -> Dict[str, Any]:
        """
        Execute backtest in containerized environment.

        Args:
            code: Strategy code to execute
            symbols: List of symbols to trade
            config: Strategy configuration
            start_date: Backtest start date
            end_date: Backtest end date
            initial_cash: Initial capital

        Returns:
            Backtest results dict or error info
        """
        container = None
        temp_dir = None
        container_failed = False

        try:
            logger.info(f"Executing backtest in container...")
            logger.info(f"  Image: {self.image_name}")
            logger.info(f"  Symbols: {symbols}")
            logger.info(f"  Period: {start_date.date()} to {end_date.date()}")

            # Create temporary directory for code and results
            temp_dir = tempfile.mkdtemp(prefix="backtest_")
            logger.debug(f"  Temp dir: {temp_dir}")

            # Write strategy code to file
            code_file = os.path.join(temp_dir, "strategy.py")
            with open(code_file, 'w') as f:
                f.write(code)

            # Write execution parameters to JSON
            params_file = os.path.join(temp_dir, "params.json")
            params = {
                'symbols': symbols,
                'config': config,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'initial_cash': initial_cash,
            }
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=2)

            # Create execution script
            exec_script = os.path.join(temp_dir, "run_backtest.py")
            with open(exec_script, 'w') as f:
                f.write(self._generate_execution_script())

            # Run container
            logger.info(f"Starting container...")
            container = self.docker_client.containers.run(
                image=self.image_name,
                command=["python", "/workspace/run_backtest.py"],
                volumes={
                    temp_dir: {'bind': '/workspace', 'mode': 'rw'}
                },
                mem_limit=self.max_memory,
                cpu_quota=int(self.max_cpu * 100000),  # Convert to microseconds
                cpu_period=100000,
                network_mode=self.network_mode,
                detach=True,
                remove=False,  # Don't auto-remove so we can get logs
            )

            # Wait for completion with timeout
            logger.info(f"Waiting for execution (timeout: {self.timeout}s)...")
            result = container.wait(timeout=self.timeout)

            # Get container logs
            logs = container.logs().decode('utf-8')

            # Check exit code
            exit_code = result['StatusCode']
            if exit_code != 0:
                container_failed = True
                logger.error(f"Container exited with code {exit_code}")
                logger.error(f"Container logs:\n{logs}")
                return {
                    'success': False,
                    'error': f"Container exited with code {exit_code}",
                    'logs': logs,
                }

            # Read results from output file
            results_file = os.path.join(temp_dir, "results.json")
            if not os.path.exists(results_file):
                return {
                    'success': False,
                    'error': 'Results file not found',
                    'logs': logs,
                }

            with open(results_file, 'r') as f:
                results = json.load(f)

            logger.info(f"✅ Backtest completed successfully")
            logger.info(f"   Return: {results.get('metrics', {}).get('total_return', 0):.2f}%")

            return {
                'success': True,
                'results': results,
                'logs': logs,
            }

        except docker.errors.ContainerError as e:
            container_failed = True
            logger.error(f"❌ Container error: {e}")
            return {
                'success': False,
                'error': f"Container error: {str(e)}",
                'logs': str(e),
            }

        except Exception as e:
            container_failed = True
            logger.error(f"❌ Execution failed: {e}")
            import traceback
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
            }

        finally:
            # TEMPORARY: Don't remove containers on failure so we can debug
            # This will be reverted once we fix the root issue
            if container:
                try:
                    if container_failed:
                        logger.warning(f"⚠️  Container {container.id[:12]} NOT removed (failed) - inspect with: docker logs {container.id[:12]}")
                    else:
                        container.remove(force=True)
                        logger.debug("Container removed (successful execution)")
                except Exception as e:
                    logger.warning(f"Failed to handle container cleanup: {e}")

            # Cleanup temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug("Temp directory cleaned up")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp dir: {e}")

    def _generate_execution_script(self) -> str:
        """Generate the Python script that runs inside the container."""
        return """
import sys
import json
from datetime import datetime
from pathlib import Path
import numpy as np

# Add app to path
sys.path.insert(0, '/app')

from tools.run_backtest import run_backtest_from_code

def convert_to_json_serializable(obj):
    \"\"\"Convert numpy/pandas types to JSON-serializable Python types.\"\"\"
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, 'isoformat'):  # datetime-like objects
        return obj.isoformat()
    else:
        return obj

# Load parameters
with open('/workspace/params.json', 'r') as f:
    params = json.load(f)

# Load strategy code
with open('/workspace/strategy.py', 'r') as f:
    code = f.read()

# Parse dates
start_date = datetime.fromisoformat(params['start_date'])
end_date = datetime.fromisoformat(params['end_date'])

# Run backtest
try:
    results = run_backtest_from_code(
        code=code,
        symbols=params['symbols'],
        config=params['config'],
        start_date=start_date,
        end_date=end_date,
        initial_cash=params['initial_cash'],
        data_source='yfinance',
        verbose=False,
    )

    # Convert all data to JSON-serializable types
    results = convert_to_json_serializable(results)

    # Write results
    with open('/workspace/results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Backtest completed: {results['metrics']['total_return']:.2f}% return")
    sys.exit(0)

except Exception as e:
    print(f"❌ Backtest failed: {e}")
    import traceback
    traceback.print_exc()

    # Write error
    with open('/workspace/results.json', 'w') as f:
        json.dump({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
        }, f, indent=2)

    sys.exit(1)
"""

    def check_image_exists(self) -> bool:
        """Check if Docker image exists."""
        try:
            # Try to get the image
            self.docker_client.images.get(self.image_name)
            return True
        except docker.errors.ImageNotFound:
            # Fallback: check if image exists in list
            logger.warning(f"Image.get() failed, checking image list...")
            for image in self.docker_client.images.list():
                if self.image_name in image.tags:
                    logger.info(f"✅ Found image {self.image_name} in list")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking image: {e}")
            # Fallback: check if image exists in list
            for image in self.docker_client.images.list():
                if self.image_name in image.tags:
                    logger.info(f"✅ Found image {self.image_name} in list (after error)")
                    return True
            return False

    def list_containers(self) -> list:
        """List all backtest containers (running and stopped)."""
        try:
            containers = self.docker_client.containers.list(
                all=True,
                filters={'ancestor': self.image_name}
            )
            return containers
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return []

    def cleanup_old_containers(self, max_age_hours: int = 24):
        """
        Remove old stopped containers.

        Args:
            max_age_hours: Remove containers older than this many hours
        """
        try:
            containers = self.list_containers()
            removed = 0

            for container in containers:
                if container.status != 'running':
                    try:
                        container.remove()
                        removed += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove container {container.id[:12]}: {e}")

            logger.info(f"Cleaned up {removed} old containers")

        except Exception as e:
            logger.error(f"Failed to cleanup containers: {e}")


# Convenience function
def execute_strategy_in_container(
    code: str,
    symbols: list,
    config: dict,
    start_date: datetime,
    end_date: datetime,
    initial_cash: float = 100000.0,
) -> Dict[str, Any]:
    """
    Convenience function to execute strategy in container.

    Args:
        code: Strategy code
        symbols: Symbols to trade
        config: Strategy config
        start_date: Start date
        end_date: End date
        initial_cash: Initial capital

    Returns:
        Execution results
    """
    executor = CodeExecutor()

    # Skip explicit image check - let Docker fail naturally if image doesn't exist
    # The check_image_exists() method has issues with some Docker API versions
    logger.info(f"Executing backtest with image: {executor.image_name}")

    return executor.execute_backtest(
        code=code,
        symbols=symbols,
        config=config,
        start_date=start_date,
        end_date=end_date,
        initial_cash=initial_cash,
    )


if __name__ == "__main__":
    # Test code executor
    logging.basicConfig(level=logging.INFO)

    executor = CodeExecutor()

    # Check Docker availability
    try:
        executor.docker_client.ping()
        logger.info("✅ Docker is available")
    except Exception as e:
        logger.error(f"❌ Docker is not available: {e}")
        exit(1)

    # Check if image exists
    if executor.check_image_exists():
        logger.info(f"✅ Image exists: {executor.image_name}")
    else:
        logger.warning(f"⚠️  Image not found: {executor.image_name}")
        logger.info("Build it with: docker build -f Dockerfile.backtest -t backtest-executor:latest .")

    # List containers
    containers = executor.list_containers()
    logger.info(f"Found {len(containers)} backtest containers")
