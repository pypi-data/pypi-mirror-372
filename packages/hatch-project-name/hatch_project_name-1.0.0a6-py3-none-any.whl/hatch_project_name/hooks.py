from hatchling.plugin import hookimpl

from hatch_project_name.plugin import ProjectNameBuildHook


@hookimpl
def hatch_register_build_hook():
    return ProjectNameBuildHook
