# All convert scripts require 2 parameters:
# automatix2xyz SOURCE_AUTOMATIX_SCRIPT TARGET_FILE_OR_DIRECTORY
import argparse
from typing import Literal

from automatix.config import bash_completion, SCRIPT_PATH, SCRIPT_FIELDS

if bash_completion:
    from automatix.config import autocomplete, ScriptFileCompleter

def arguments(target_type: Literal['markdown']) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Automation wrapper for bash and python commands.',
        epilog='Explanations and README at https://github.com/vanadinit/automatix_cmd',
    )
    scriptfile_action = parser.add_argument(
        'scriptfile',
        help='Path to scriptfile (yaml)',
    )
    if bash_completion:
        scriptfile_action.completer = ScriptFileCompleter(script_path=SCRIPT_PATH)

    parser.add_argument(
        'target',
        help=f'Path to target {target_type} file',
    )

    if bash_completion:
        autocomplete(parser)
    return parser.parse_args()