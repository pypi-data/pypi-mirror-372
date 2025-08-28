import sys
from .utilities import launch_blender, launch_unreal
app_name = sys.argv[1]
app_version = sys.argv[2]
debug_on = sys.argv[3]


if __name__ == '__main__':
    debug_on = '1' if debug_on.lower() == 'yes' else '0'

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