from fastpluggy.core.database import session_scope
from fastpluggy.core.tools.serialize_tools import serialize_value
from ..models.context import TaskContextDB
from ..schema.context import TaskContext


def save_context(context: TaskContext) -> None:
    """
    Persist a TaskContext to the database.
    """

    data = serialize_value(context.to_dict())
    data.pop('thread_handler')

    with session_scope() as db:
        data = TaskContextDB(**data)
        db.add(data)
        db.commit()

