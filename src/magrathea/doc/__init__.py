"""
Describe purpose of this script here

Created: 9/19/25
"""
from IPython.core.display_functions import display
from IPython.display import Markdown

def extract_literate_code(file_path, section_id=None):
    """Extract code between begin_literate_display and end_literate_display for a given section_id."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    if section_id is None:
        return "".join(lines)
    result = []
    capturing = False
    for line in lines:
        if f'# begin literate_doc {section_id}' in line:
            capturing = True
            continue
        if f'# end literate_doc {section_id}' in line:
            capturing = False
            continue
        if capturing:
            result.append(line)
    return ''.join(result)


def display_literate_code(file_path,section_id=None,language="python"):
    code=extract_literate_code(file_path,section_id)
    display(Markdown(f"```{language}\n{code}\n```"))
