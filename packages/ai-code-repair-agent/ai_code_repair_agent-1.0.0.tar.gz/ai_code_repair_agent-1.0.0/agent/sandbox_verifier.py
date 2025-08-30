import docker
import os
import shutil
import time
import logging
import uuid
import ast
from typing import Tuple, List, Set
from stdlib_list import stdlib_list

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SandboxVerifier:

    def __init__(self, original_app_path: str):
        self.client = docker.from_env()
        self.original_app_path = original_app_path
        self.session_id = str(uuid.uuid4())[:8]
        self.temp_dir = f"temp_verification_{self.session_id}"
        self.image_tag = f"verifier-image-{self.session_id}"
        self.container_name = f"verifier-container-{self.session_id}"
        self.python_version = "3.9"
        self.standard_libs = stdlib_list(self.python_version)

    def _discover_dependencies(self, file_path: str) -> Set[str]:
        dependencies = set()
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read(), filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_module = alias.name.split('.')[0]
                        if root_module not in self.standard_libs:
                            dependencies.add(root_module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        root_module = node.module.split('.')[0]
                        if root_module not in self.standard_libs:
                            dependencies.add(root_module)
        except Exception as e:
            logging.error(f"[{self.session_id}] Failed to parse dependencies from {file_path}: {e}")
        
        logging.info(f"[{self.session_id}] Discovered dependencies: {dependencies}")
        return dependencies

    def _generate_dockerfile(self, entrypoint_script: str) -> str:
        return f"""
FROM python:{self.python_version}-slim
WORKDIR /app
COPY requirements.txt .
RUN if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
COPY . .
CMD ["python", "{entrypoint_script}"]
"""

    def _setup_temp_environment(self, original_code: str, patched_code: str, entrypoint_script: str) -> bool:
        try:
            logging.info(f"[{self.session_id}] Setting up temporary environment at {self.temp_dir}")
            shutil.copytree(self.original_app_path, self.temp_dir)
            
            source_file_path = os.path.join(self.temp_dir, entrypoint_script)
            if not os.path.exists(source_file_path):
                logging.error(f"[{self.session_id}] Entrypoint script '{entrypoint_script}' not found in the project.")
                return False

            with open(source_file_path, 'r') as f:
                content = f.read()
            
            if original_code not in content:
                logging.error(f"[{self.session_id}] Original code snippet not found in the source file. Cannot apply patch.")
                return False

            patched_content = content.replace(original_code, patched_code)
            with open(source_file_path, 'w') as f: f.write(patched_content)
            logging.info(f"[{self.session_id}] Successfully applied patch to temporary file.")

            dockerfile_path = os.path.join(self.temp_dir, 'Dockerfile')
            if not os.path.exists(dockerfile_path):
                logging.warning(f"[{self.session_id}] No Dockerfile found. Starting auto-discovery...")
                
                deps = self._discover_dependencies(source_file_path)

                req_path = os.path.join(self.temp_dir, 'requirements.txt')
                with open(req_path, 'w') as f:
                    for dep in deps:
                        f.write(f"{dep}\n")
                logging.info(f"[{self.session_id}] Auto-generated requirements.txt.")

                dockerfile_content = self._generate_dockerfile(entrypoint_script)
                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile_content)
                logging.info(f"[{self.session_id}] Auto-generated Dockerfile.")

            return True
        except Exception as e:
            logging.error(f"[{self.session_id}] Failed to set up temp environment: {e}")
            return False

    def _build_docker_image(self) -> bool:
        try:
            logging.info(f"[{self.session_id}] Building Docker image: {self.image_tag}")
            self.client.images.build(path=self.temp_dir, tag=self.image_tag, rm=True)
            logging.info(f"[{self.session_id}] Docker image built successfully.")
            return True
        except docker.errors.BuildError as e:
            logging.error(f"[{self.session_id}] Docker build failed. Log:")
            for line in e.build_log:
                if 'stream' in line: print(line['stream'].strip())
            return False
        except Exception as e:
            logging.error(f"[{self.session_id}] An unexpected error occurred during image build: {e}")
            return False

    def _run_test(self, test_command: List[str]) -> Tuple[bool, str]:
        container = None
        try:
            logging.info(f"[{self.session_id}] Running container to execute the script...")
            logs = self.client.containers.run(
                self.image_tag,
                name=self.container_name,
                remove=True
            )
            output = logs.decode('utf-8').strip()
            logging.info(f"[{self.session_id}] Script output: {output}")

            if "Traceback" not in output:
                return True, "Test passed: No traceback found in script output."
            else:
                return False, f"Test failed: Traceback found in output.\n{output}"
        except docker.errors.ContainerError as e:
             output = e.stderr.decode('utf-8').strip()
             logging.error(f"[{self.session_id}] Container exited with an error: {output}")
             return False, f"Test failed: Container exited with an error.\n{output}"
        except Exception as e:
            logging.error(f"[{self.session_id}] An error occurred during the test run: {e}")
            return False, str(e)

    def _cleanup(self):
        logging.info(f"[{self.session_id}] Cleaning up resources...")
        try:
            if os.path.exists(self.temp_dir): shutil.rmtree(self.temp_dir)
            self.client.images.remove(self.image_tag, force=True)
        except docker.errors.ImageNotFound: pass
        except Exception as e: logging.error(f"[{self.session_id}] Error during cleanup: {e}")

    def verify_fix(self, original_code: str, patched_code: str, entrypoint_script: str, test_command: List[str]) -> bool:
        if not self._setup_temp_environment(original_code, patched_code, entrypoint_script):
            self._cleanup()
            return False
        
        if not self._build_docker_image():
            self._cleanup()
            return False
        
        success, message = self._run_test(test_command)
        logging.info(f"[{self.session_id}] Verification result: {success} - {message}")
        
        self._cleanup()
        return success
