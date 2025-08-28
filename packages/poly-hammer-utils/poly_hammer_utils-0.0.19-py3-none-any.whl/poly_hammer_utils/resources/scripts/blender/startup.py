import os
import sys
import bpy
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

if int(os.environ.get('BLENDER_DEBUGGING_ON', '0')):
    try:
        import debugpy
        port = int(os.environ.get('BLENDER_DEBUG_PORT', 5678))
        debugpy.configure(python=sys.executable)
        debugpy.listen(port)
        logger.info(f'Waiting for debugger to attach on port {port}...')
        debugpy.wait_for_client()
    except ImportError:
        logger.error(
            'Failed to initialize debugger because debugpy is not available '
            'in the current python environment.'
        )

BLENDER_SCRIPTS_FOLDERS = [Path(i) for i in os.environ.get('BLENDER_SCRIPTS_FOLDERS', '').split(os.pathsep)]

for scripts_folder in BLENDER_SCRIPTS_FOLDERS:
    script_directory = bpy.context.preferences.filepaths.script_directories.get(scripts_folder.parent.name)
    if script_directory:
        bpy.context.preferences.filepaths.script_directories.remove(script_directory)

    script_directory = bpy.context.preferences.filepaths.script_directories.new()
    script_directory.name = scripts_folder.parent.name
    script_directory.directory = str(scripts_folder)
    sys.path.append(str(scripts_folder))


try:
    bpy.ops.script.reload()
except ValueError:
    pass

for scripts_folder in BLENDER_SCRIPTS_FOLDERS:
    for addon in os.listdir(scripts_folder / 'addons'):
        if (scripts_folder / 'addons' / addon).is_dir():
            bpy.ops.preferences.addon_enable(module=addon)