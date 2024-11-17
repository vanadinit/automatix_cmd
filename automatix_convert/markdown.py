from automatix import get_script
from automatix.command import parse_key
from . import arguments

SECTION_HEADER = ''
SECTION_DIVIDER = ''
CODE = ''

def main():
    args = arguments('markdown')
    script = get_script(args=args)
    target_file_path = args.target

    content = f'# {script.get('name')}\n'
    content += '* * *\n' # horizontal line
    if systems := script.get('systems'):
        content += '## Systems\n'
        content += '| Name | Address |\n| ------ | ------ |\n'
        for name, address in systems.items():
            content += f'| {name} | {address} |\n'

    if variables := script.get('vars'):
        content += '## Parameters\n'
        content += '| Name | Value |\n| ------ | ------ |\n'
        for name, value in variables.items():
            content += f'| {name} | {value} |\n'

    for cmd_key, cmd_value in script['pipeline'].items():
        condition_var, assignment_var, key = parse_key(cmd_key)
        raise NotImplemented
