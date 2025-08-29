from os import path

this_directory = path.dirname(__file__)
version_file = path.join(this_directory, 'VERSION')

def _read_version():
    with open(version_file) as file:
        return file.readline().strip()

def _read_git_sha():
    with open(version_file) as file:
        lines = file.readlines()
        if len(lines) > 1:
            return lines[1].strip()

    return None
