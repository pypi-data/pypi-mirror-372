# Frequenz Core Library Release Notes

## New Features

- A new `frequenz.core.enum` module was added, providing a drop-in replacement `Enum` that supports deprecating members.

   Example:

   ```python
   from frequenz.core.enum import Enum, DeprecatedMember

   class TaskStatus(Enum):
       OPEN = 1
       IN_PROGRESS = 2
       PENDING = DeprecatedMember(1, "PENDING is deprecated, use OPEN instead")
       DONE = DeprecatedMember(3, "DONE is deprecated, use FINISHED instead")
       FINISHED = 4

   status1 = TaskStatus.PENDING  # Warns: "PENDING is deprecated, use OPEN instead"
   assert status1 is TaskStatus.OPEN
   ```
