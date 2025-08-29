import inspect
from typing import Any, Callable, NamedTuple, TypeAlias, TypeVar

CommandFn1: TypeAlias = Callable[[], Any]
CommandFn2: TypeAlias = Callable[[Any], Any]
CommandFn: TypeAlias = CommandFn1 | CommandFn2
WrappedFn: TypeAlias = TypeVar("WrappedFn", bound=CommandFn)


FullQualifiedPathStr: TypeAlias = str
ActionStr: TypeAlias = str

command_registry: dict[FullQualifiedPathStr, ActionStr] = {}


def fully_qualified_name(obj: object) -> FullQualifiedPathStr:
    """
    Return the fully-qualified name of the given object.

    :param obj: An object, such as a class or an instance
    :return: The fully qualified name of the object using the __module__ and __qualname__ attributes.
    """
    return obj.__module__ + "." + obj.__qualname__


def split_module_path(path: FullQualifiedPathStr) -> tuple[str, str]:
    """Split module path into parent and name"""
    parts = path.split(".")
    parent = ".".join(parts[:-1])
    name = parts[-1]
    return parent, name


def register_command(action: str) -> Callable[[WrappedFn], WrappedFn]:
    """
    Register a method as a custom command.

    This decorator is used to register a method as a custom command that can be invoked by the connector.
    The method must accept exactly one argument, which will be the body (or payload) of the command.

    Example usage:

    .. code-block:: python

    class MyConnector(Connector):
        @register_command("my.custom.action")
        def my_custom_action(self, body: str):
            return f"Action called with body: {body}"


    Example command request. See https://developers.tetrascience.com/reference/ag-create-command for more information on
    how to send command requests.

    .. code-block::

        {
          "expiresAt": "2025-01-31T23:58:43.749Z",
          "payload": {
            "foo": "bar"
          },
          "payloadDelivery": "embedded",
          "action": "my.custom.action",
          "targetId": "7982e5c6-16bf-4f5b-af06-47f3380ca85a"
        }


    :param action: The action name to register the method under. This must be a string.
    :return: The decorated method.
    :raises TypeError: If the decorator is used without an action string or if the action is not a string.
    """
    if (
        inspect.ismethod(action)
        or inspect.isfunction(action)
        or isinstance(action, staticmethod)
        or isinstance(action, classmethod)
    ):
        # give a useful warning if developers accidentally use this as a bare decorator
        raise TypeError(
            f"{register_command.__name__} cannot be used as a bare decorator. Must provide an action as a string as "
            f"in `@{register_command.__name__}('myaction')`"
        )
    if not isinstance(action, str):
        raise TypeError(f"Action must be a string, found a `{type(action)}`")

    def add_to_command_registry(fn: WrappedFn) -> WrappedFn:
        key = fully_qualified_name(fn)
        command_registry[key] = action
        return fn

    return add_to_command_registry


class CustomCommand(NamedTuple):

    action: ActionStr
    callable: Callable


CommandsByActionDict: TypeAlias = dict[ActionStr, CustomCommand]


def collect_commands_by_actions(inst: Any) -> CommandsByActionDict:
    """
    Collects registered methods owned by an instance, returns
    a dictionary of registered methods keyed by their action name.

    :param inst: The instance object that must have a `__class__` attribute defined.
    :return: A dictionary of registered commands keyed by their action name.
    """

    methods_by_action = {}

    # iterate over parent classes in reverse using the method order resolution
    # so that we can get inherited registered actions. As a result of this
    # we also override inherited actions if devs registered the same action
    # in a ChildClass
    mro = inspect.getmro(inst.__class__)
    for clazz in reversed(mro):
        class_name = fully_qualified_name(clazz)
        for full_path, action in command_registry.items():
            owning_class, method_name = split_module_path(full_path)

            # if class names match, this indicates the registered method
            # is "owned" by the class provided.
            if class_name == owning_class:
                methods_by_action[action] = CustomCommand(
                    action=action,
                    callable=getattr(inst, method_name),
                )
    return methods_by_action
