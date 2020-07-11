from pkg_resources import resource_string


def read_resource(filename, path=None):
    resource_path = 'arbie.resources'
    if path:
        resource_path += '.' + path
    return resource_string(resource_path, filename).decode("utf-8")


def readResource(self, path, filename):
    return resource_string(f"arbie.resources.{path}", filename).decode("utf-8")
