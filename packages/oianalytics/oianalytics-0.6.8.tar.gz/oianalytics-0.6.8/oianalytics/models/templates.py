import importlib.resources as pkg_resources

from . import _template_resources


# List templates
def available_templates():
    return ["free_from_api", "single_observation", "file_processing"]


# Show templates
def get_template(template: str):
    """
    Read the source code of a template file

    Parameters
    ----------
    template: str
        Name of the template. Can be 'free_from_api', 'single_observation' or 'file_processing'.

    Returns
    -------
    The source code string of the template
    """

    return pkg_resources.read_text(_template_resources, f"{template}_template.py")


def print_template(template: str):
    """
    Print the source code of a template file

    Parameters
    ----------
    template: str
        Name of the template. Can be 'free_from_api', 'single_observation' or 'file_processing'.

    Returns
    -------
    Doesn't return outputs. Prints the source code string of the template.
    """

    print(get_template(template=template))
