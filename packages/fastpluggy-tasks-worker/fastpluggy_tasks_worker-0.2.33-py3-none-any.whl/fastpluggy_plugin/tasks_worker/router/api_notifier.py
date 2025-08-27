from fastapi import APIRouter

from ..notifiers.registry import get_global_notification_rules

api_notifier_router = APIRouter(
    prefix='/api/notifiers',
)


@api_notifier_router.get("/", name="list_available_notifiers")
def list_available_notifiers():
    from ..notifiers.registry import get_notifier_registry

    registry = get_notifier_registry()
    default_rules = get_global_notification_rules()
    result = {'available_notifiers': [], 'default_rules': default_rules}

    for name, config in registry.items():
        result['available_notifiers'].append({
            "name": name,
            "events": config.get("configurable_events", []),
        })

    return result
