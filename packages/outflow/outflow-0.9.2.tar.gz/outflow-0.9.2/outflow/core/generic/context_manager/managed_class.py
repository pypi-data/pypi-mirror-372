# -*- coding: utf-8 -*-
class ManagedClassException(Exception):
    pass


class Manager:
    """Store instances of a managed class and expose iterable-like methods"""

    def __init__(self):
        self.instances = []
        self.instances_by_name = {}

    def __getitem__(self, name):
        """
        Get an instance from the manager given only its name, as it was a
        dictionary.
        """
        return self.instances_by_name[name]

    def __contains__(self, name):
        """
        Check if the manager contains a given instance by its name.
        """
        return name in self.instances_by_name

    def __iter__(self):
        """
        Iter over all the class instances
        """
        return iter(self.instances)


class ManagedClassMeta(type):
    def __call__(cls, *args, **kwargs):
        """Call register after instance __init__"""
        instance = super().__call__(*args, **kwargs)
        registered_instance = instance.register()
        return registered_instance

    def __iter__(self):
        """
        Iter over all the class instances
        """
        self.raise_if_outside_context_manager()
        return iter(self.manager.instances)

    def __len__(self):
        self.raise_if_outside_context_manager()
        return len(self.manager.instances)

    def raise_if_outside_context_manager(self):
        if self.context_manager is None:
            raise ManagedClassException(
                "A managed class must be instanciated within its manager context"
            )

    @property
    def context_manager(self):
        return self.manager_class.get_context()

    @property
    def manager(self):
        self.raise_if_outside_context_manager()
        return self.context_manager.setdefault(self.__name__, Manager())


class ManagedClass(metaclass=ManagedClassMeta):
    """Store class instances in a local context and expose class level iterable-like methods directly"""

    manager_class = None

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)

        cls.raise_if_outside_context_manager()

        return instance

    @property
    def manager(self):
        """Shortcut for the class property 'manager'"""
        return self.__class__.manager

    def __init_subclass__(cls, *args, context_manager, **kwargs):
        super().__init_subclass__()
        cls.manager_class = context_manager

    def register(self):
        if not hasattr(self, "name"):
            raise AttributeError(
                f"'{self.__class__}' instance must have a 'name' attribute"
            )

        # get previous instance with the same name, if any, and return it
        if self.name in self.manager.instances_by_name:
            previous_instance = self.manager.instances_by_name[self.name]
            return previous_instance

        # else, register the new instance in the instances dict and list
        self.manager.instances_by_name[self.name] = self
        self.manager.instances.append(self)
        return self

    @classmethod
    def remove(cls, instance):
        if hasattr(instance, "name"):
            if instance.name in instance.manager.instances_by_name:
                del instance.manager.instances_by_name[instance.name]
        instance.manager.instances.remove(instance)
