# -*- coding: utf-8 -*-
import os
import pathlib
import shutil
import stat
import sys
from datetime import date
from os import path
from pprint import pformat

import jinja2
import outflow
from outflow.core.commands import argument
from outflow.core.logging import logger

from .management import Management


def render(template_filepath, context):
    template_path, filename = os.path.split(template_filepath)
    return (
        jinja2.Environment(loader=jinja2.FileSystemLoader(template_path or "./"))
        .get_template(filename)
        .render(context)
    )


def make_writeable(filename):
    """
    Make sure that the file is writeable.
    Useful if our source is read-only.
    """
    if sys.platform.startswith("java"):
        # On Jython there is no os.access()
        return
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)


def create_from_template(pipeline_or_plugin, name, directory, namespace=None):
    """
    Create pipeline/plugin directory tree from POPPy templates

    :param pipeline_or_plugin: String indicating which template to use ('pipeline' or 'plugin')
    :param name: name of the pipeline/plugin
    :param directory: path to the plugin/pipeline directory
    :return:
    """
    base_subdir = "%s_template" % pipeline_or_plugin

    # store the template dir path
    template_dir = (
        pathlib.Path(__file__).parent.parent.resolve() / "templates" / base_subdir
    ).as_posix()

    prefix_length = len(template_dir) + 1

    # if some directory is given, make sure it's nicely expanded
    if directory is None:
        top_dir = path.join(os.getcwd(), name)
        try:
            os.makedirs(top_dir)
        except FileExistsError:
            raise FileExistsError("'%s' already exists" % top_dir)
        except OSError as e:
            raise OSError(e)
    else:
        top_dir = os.path.abspath(path.expanduser(directory))
        os.makedirs(top_dir, exist_ok=True)

    if pipeline_or_plugin == "pipeline":
        # create the 'plugins' directory
        os.makedirs(path.join(top_dir, "plugins"))

    base_name = "%s_name" % pipeline_or_plugin
    base_directory = "%s_directory" % pipeline_or_plugin
    camel_case_name = "camel_case_%s_name" % pipeline_or_plugin
    camel_case_value = "".join(x for x in name.title() if x != "_")
    databases = [
        {
            "identifier": "default",
            "dialect": "postgresql",
            "name": "pipe_db",
            "host": "localhost",
            "admin_account": "pipeadmin",
            "admin_password": "adminpwd",
            "user_account": "pipeuser",
            "user_password": "userpwd",
            "short_description": "Pipeline database",
            "description": "Pipeline Database",
            "release": {
                "author": "My team",
                "date": date.today().strftime("%Y-%m-%d"),
                "institute": "Unknown",
                "reference": "Framework_User_Manual",
                "version": "0.1.0",
                "modification": "",
            },
        }
    ]

    context = {
        base_name: name,
        base_directory: top_dir,
        camel_case_name: camel_case_value,
        "plugin_namespace": namespace,
        "outflow_version": outflow.__version__,
        "provider": "Unknown",
        "release_date": date.today().strftime("%Y-%m-%d"),
        "databases": databases,
        "databases_with_description": [x for x in databases if "description" in x],
    }

    logger.debug("context: %s" % pformat(context))

    for root, dirs, files in os.walk(template_dir):
        path_rest = root[prefix_length:]

        # create relative filepath
        if namespace is not None:
            relative_dir = path_rest.replace("plugin_namespace", namespace).replace(
                base_name, name
            )
        else:
            relative_dir = path_rest.replace(base_name, name)
        if relative_dir:
            target_dir = path.join(top_dir, relative_dir)
            if not path.exists(target_dir):
                os.mkdir(target_dir)

        # ignore pycache and hidden directories
        for dir_name in dirs[:]:
            if dir_name.startswith(".") or dir_name == "__pycache__":
                dirs.remove(dir_name)

        for filename in files:
            if filename.endswith((".pyo", ".pyc", ".py.class")):
                # ignore some files as they cause various breakages.
                continue
            old_path = path.join(root, filename)
            if filename.endswith(".j2"):
                new_filename = filename[:-3]
            else:
                new_filename = filename

            new_path = path.join(
                top_dir, relative_dir, new_filename.replace(base_name, name)
            )

            if path.exists(new_path):
                raise FileExistsError(
                    "%s already exists, overlaying a "
                    "project or app into an existing "
                    "directory won't replace conflicting "
                    "files" % new_path
                )

            if filename.endswith(".j2"):
                content = render(old_path, context)
                with open(new_path, "w", encoding="utf-8") as new_file:
                    new_file.write(content)
            else:
                shutil.copyfile(old_path, new_path)

                logger.debug("Creating %s\n" % new_path)
            try:
                shutil.copymode(old_path, new_path)
                make_writeable(new_path)
            except OSError:
                logger.error(
                    "Notice: Couldn't set permission bits on %s. You're "
                    "probably using an uncommon filesystem setup. No "
                    "problem." % new_path
                )


@Management.subcommand(invokable=False)
def Create():
    pass


@argument("name", help="Name of the pipeline")
@Create.subcommand(description="Create a new pipeline")
@argument("--pipeline_dir", help="Optional destination directory")
def Pipeline(name, pipeline_dir):
    create_from_template("pipeline", name, pipeline_dir)
    logger.info(f"Pipeline '{name}' successfully created")


@Create.subcommand(description="Create a new plugin")
@argument("name", help="Name of the plugin")
@argument("--plugin_dir", help="Optional destination directory")
@argument("--namespace", help="Plugin namespace")
@argument("--cython", action="store_true", help="Create a Cython-ready plugin")
def Plugin(name, plugin_dir, namespace, cython):
    if name.count(".") > 1:
        raise ValueError(f"{name} has more than one 'dot' character")

    if "." in name:
        split_name = name.split(".")
        namespace = split_name[0]
        name = split_name[1]

    if namespace is None:
        # FIXME
        raise NotImplementedError("Plugins without namespace are not yet supported")

    create_from_template("plugin", name, plugin_dir, namespace)

    logger.info(f"Plugin '{name}' successfully created")
