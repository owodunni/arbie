"""File reading helper functions."""
from pkg_resources import resource_string


def read_resource(filename, path=None):
    resource_path = "arbie.resources"
    if path:
        resource_path = f"{resource_path}.{path}"
    return resource_string(resource_path, filename).decode("utf-8")
