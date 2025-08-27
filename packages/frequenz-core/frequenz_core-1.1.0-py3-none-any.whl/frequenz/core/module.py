# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Tools for dealing with Python modules."""


def get_public_module_name(module_name: str) -> str | None:
    """Get the name of the public module containing the given module name.

    * Modules are considered private if they start with `_`.
    * All modules inside a private module are also considered private, even if they
      don't start with `_`.
    * If there is no leading public part, `None` is returned.

    Example:
        Here are a few examples of how this function will resolve module names:

        * `some.pub` -> `some.pub`
        * `some.pub._some._priv` -> `some.pub`
        * `some.pub._some._priv.public` -> `some.pub`
        * `some.pub._some._priv.public._private` -> `some.pub`
        * `_priv` -> `None`

    Args:
        module_name: The fully qualified name of the module to get the public name for
            (normally the `__name__` built-in variable).

    Returns:
        The name of the public module containing the given module name.
    """
    public_parts: list[str] = []
    for part in module_name.split("."):
        if part.startswith("_"):
            break
        public_parts.append(part)
    return ".".join(public_parts) or None
