# -*- coding: utf-8 -*-
import inspect

from declic import Command as DeclicCommand
from declic import Group
from outflow.core.generic.metaclasses import Singleton
from outflow.core.generic.string import to_camel_case, to_snake_case
from outflow.core.logging import logger
from outflow.core.pipeline import context
from outflow.core.tasks import Task
from outflow.library.tasks.pipeline_args import PipelineArgs


class Command(Group, metaclass=Singleton):
    """
    Outflow base command
    """

    def __init__(
        self,
        *args,
        invokable=True,
        on_before=None,
        db_untracked=False,
        backend=None,
        **kwargs,
    ):
        """Bypass the Group command init to avoid subparser instantiation if not needed

        Args:
            invokable (bool, optional): If False, show the help message when called and exit. Defaults to True.
            on_before ([type], optional): Callback called just before the task flow run. Defaults to None.
        """
        logger.debug(f"Initialize command '{self.__class__.__name__}'")

        self.allow_extra_args = False

        if kwargs.pop("allow_extra_args", False):
            self.allow_extra_args = True

        self.commands = {}
        self._subparsers = None

        # this function will be called before each invoke of the group
        # even if the group is not invokable
        self._on_before = on_before

        DeclicCommand.__init__(
            self,
            *args,
            name=to_snake_case(self.__class__.__name__),
            **kwargs,
        )
        self.add_arguments()

        self.invokable = invokable
        self.db_untracked = db_untracked
        self.backend = backend
        self.parser.description = self.__doc__

    @property
    def subparsers(self):
        """Initialize and get the argparse subparser

        Note: CLI positional arguments are not available for commands with associated subcommands

        TODO: implement this property in declic
        """
        if self._subparsers is None:
            self._subparsers = self.parser.add_subparsers()
        return self._subparsers

    def invoke(self, args, extra_args):
        """
        Overrides invoke from declic.Group to call directly the main actor run method
        """

        # TODO: add chain support using the parent task list

        if not self.invokable:
            self.print_help()
            return 0  # TODO manage this case

        if not self.allow_extra_args and extra_args:
            error_msg = (
                f"Unrecognized arguments: {' '.join(extra_args)} in command"
                f" {self.name}. If passing these arguments to your task is "
                f'intended behaviour, use "allow_extra_args=True" in the '
                f"subcommands decorator arguments"
            )
            raise Exception(error_msg)

        return self

    def parse_command_tree(self, argv=None):
        args, extra_args = self.parser.parse_known_args(argv)

        # update the pipeline context with the CLI args
        context.args = args
        context.extra_args = extra_args
        return args.__declic_invoke_function__(args, extra_args=extra_args)

    def parser_add_mutually_exclusive_group(self, *args, **kwargs):
        return self.parser.add_mutually_exclusive_group(*args, **kwargs)

    def add_arguments(self):
        pass

    def setup_tasks(self):
        pass

    @classmethod
    def subcommand(cls, *args, name=None, **kwargs):
        """
        A decorator to declare a subcommand
        """

        with_task_context = kwargs.pop("with_task_context", False)

        def decorator(callback_or_command_class):
            is_class = inspect.isclass(callback_or_command_class)
            self = cls()

            if is_class:
                # use the given command class as subclass
                if not issubclass(callback_or_command_class, Command):
                    raise Exception(f"The command shall be a subclass of {Command}")
                SubClass = callback_or_command_class
            else:
                # generate a new command with a single task on the fly using the callback function
                subclass_name = (
                    callback_or_command_class.__name__ if name is None else name
                )

                def add_arguments(self):
                    # get command parameters

                    callback = callback_or_command_class

                    try:
                        params = callback.__cli_params__
                    except AttributeError:
                        params = []

                    # add parameters to the parser
                    for param_args, param_kwargs in params:
                        self.add_argument(*param_args, **param_kwargs)

                def setup_tasks(self):
                    pipeline_args = PipelineArgs()

                    command_self = self

                    class InnerTask(Task):
                        def __init_subclass__(cls, **kwargs):
                            cls.with_self = with_task_context
                            super().__init_subclass__(**kwargs)

                        def __init__(self, **kwargs):
                            super().__init__(
                                **kwargs,
                                name=subclass_name,
                            )

                        def setup_targets(self):
                            pass

                        def add_upstream(self, upstream_block: "Block"):
                            self.inputs.update(upstream_block.outputs)
                            super().add_upstream(upstream_block)

                        def run(self, *args, **kwargs):
                            self.outputs = (
                                {}
                            )  # revert workaround to have normal behaviour
                            if args:
                                kwargs.update({"self": args[0]})
                            # filter task kwargs using subcommand keywords
                            return command_self.generic_callback(
                                kwargs, callback_or_command_class
                            )

                    task = InnerTask()
                    pipeline_args >> task
                    return [task]

                SubClass = type(
                    to_camel_case(subclass_name),
                    (Command,),
                    {"setup_tasks": setup_tasks, "add_arguments": add_arguments},
                )
            kwargs.setdefault("db_untracked", self.db_untracked)
            kwargs.setdefault("backend", self.backend)
            if name:
                SubClass.__name__ = name
            SubClass.__doc__ = callback_or_command_class.__doc__
            cmd = SubClass(*args, parent=self, **kwargs)
            self.add_command(cmd)
            return SubClass

        return decorator

    @property
    def full_name(self):
        """
        Returns the fully qualified command name
        """

        full_name = [self.name]

        command = self

        while command.parent and command.parent.name != "root_command":
            full_name.append(command.parent.name)
            command = command.parent

        full_name.reverse()

        return " ".join(full_name)
