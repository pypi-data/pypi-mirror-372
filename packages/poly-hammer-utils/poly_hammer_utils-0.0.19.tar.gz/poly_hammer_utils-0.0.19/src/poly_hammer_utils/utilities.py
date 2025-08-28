import os
import sys
import site
import subprocess
import dotenv
import poly_hammer_utils
from pathlib import Path
from poly_hammer_utils.constants import BLENDER_STARTUP_SCRIPT

REPO_ROOT = Path(__file__).parent.parent.parent.parent
UNREAL_PROJECT  =  Path(os.environ.get('UNREAL_PROJECT', ''))
UNREAL_EXE  =  os.environ.get('UNREAL_EXE')
UNREAL_STARTUP_SCRIPT = Path(__file__).parent / 'resources' / 'scripts' / 'unreal' / 'init_unreal.py'

dotenv.load_dotenv()


def shell(command: str, **kwargs):
    """
    Runs the command is a fully qualified shell.

    Args:
        command (str): A command.

    Raises:
        OSError: The error cause by the shell.
    """
    process = subprocess.Popen(
        command,
        shell=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs
    )

    output = []
    for line in iter(process.stdout.readline, ""): # type: ignore
        output += [line.rstrip()]
        sys.stdout.write(line)

    process.wait()

    if process.returncode != 0:
        raise OSError("\n".join(output))
        

def launch_blender(version: str, debug: str):
    if sys.platform == 'win32':
        exe_path = rf"C:\Program Files\Blender Foundation\Blender {version}\blender.exe"
    elif sys.platform == 'darwin':
        exe_path = '/Applications/Blender.app/Contents/MacOS/Blender'
    elif sys.platform == 'linux':
        exe_path = '/snap/bin/blender'
    else:
        raise OSError('Unsupported platform! Cant launch Blender.')

    if exe_path:
        command = f'"{exe_path}" --python-use-system-env --python "{BLENDER_STARTUP_SCRIPT}"'
        shell(
            command, 
            env={
                **os.environ.copy(), 
                'PYTHONUNBUFFERED': '1',
                'BLENDER_APP_VERSION': version,
                'BLENDER_DEBUGGING_ON': debug,
                'PYTHONPATH': os.pathsep.join(
                    site.getsitepackages() + [str(Path(poly_hammer_utils.__file__).parent.parent)]
                )
            }
        )


def launch_unreal(version: str, debug: str):
    if sys.platform == 'win32':
        exe_path = rf'C:\Program Files\Epic Games\UE_{version}\Engine\Binaries\Win64\UnrealEditor.exe'
    # elif sys.platform == 'darwin':
    #     exe_path = None
    # elif sys.platform == 'linux':
    #     exe_path = None
    else:
        raise OSError('Unsupported platform! Cant launch Unreal Engine.')

    if UNREAL_EXE:
        exe_path = UNREAL_EXE

    if not UNREAL_PROJECT.exists():
        raise FileNotFoundError('Unreal project not found! Please set the environment variable "UNREAL_PROJECT" to the project path.')

    if exe_path:
        command = f'"{exe_path}" "{UNREAL_PROJECT}" -stdout -nopause -forcelogflush -verbose'
        shell(
            command, 
            env={
                **os.environ.copy(),
                'UNREAL_APP_VERSION': version,
                'UNREAL_DEBUGGING_ON': debug,
                'UE_PYTHONPATH': os.pathsep.join([
                    *site.getsitepackages(),
                    str(Path(poly_hammer_utils.__file__).parent.parent.absolute()), 
                    str(UNREAL_STARTUP_SCRIPT.parent.absolute())
                ])
            }
        )


if __name__ == "__main__":
    app_name = sys.argv[1]
    app_version = sys.argv[2]
    debug_on = sys.argv[3]

    if app_name == 'blender':
        launch_blender(
            version=app_version,
            debug=debug_on
        )

    if app_name == 'unreal':
        launch_unreal(
            version=app_version,
            debug=debug_on
        )