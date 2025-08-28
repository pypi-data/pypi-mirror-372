import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


if int(os.environ.get('UNREAL_DEBUGGING_ON', '0')):
    import debugpy
    platform_folder = 'Linux'
    if sys.platform == 'win32':
        platform_folder = 'Win64'

    port = int(os.environ.get('UNREAL_DEBUG_PORT', 5678))
    python_exe_path = Path(sys.executable).parent.parent / 'ThirdParty' / 'Python3' / platform_folder / 'python'
    debugpy.configure(python=os.environ.get('UNREAL_PYTHON_EXE', str(python_exe_path)))
    debugpy.listen(port)
    logger.info(f'Waiting for debugger to attach on port {port}...')
    debugpy.wait_for_client()