import importlib
from logging import LogRecord
from typing import List, Any
from typing import Optional, Dict

from fastpluggy.core.database import get_db
from fastpluggy.fastpluggy import FastPluggy

from ..notifiers.base import BaseNotifier
from ..notifiers.base import NotificationEvent, LogStreamEvent
from ..schema.context import TaskContext
from ..schema.task_event import TaskEvent, event_matches


def get_notifier_registry() -> Dict[str, BaseNotifier]:
    return FastPluggy.get_global("notifier_registry", default={})


def get_global_notification_rules() -> List[dict]:
    return FastPluggy.get_global("global_notification_rules", default=[])


def register_notifier(notifier: BaseNotifier):
    # Save notifier in registry
    registry = get_notifier_registry()
    if notifier.name in registry:
        print(f"[WARNING] Overwriting notifier: {notifier.name}")

    notifier_factory_param = notifier.export_for_factory()
    registry[notifier.name] = notifier_factory_param

    # If it handles logs, register in log_notifiers
    if notifier_factory_param['can_handle_log']:
        print(f"[INFO] Registering log-capable notifier: {notifier.name}")

    FastPluggy.register_global("notifier_registry", registry)


def register_global_notification_rules(rules: List[dict]):
    """
    Add new global notification rules without overriding existing ones.

    Example:
    rules = [
        {
            "name": "console_notifier",
            "events": ["task_failed", "logs"]
        }
    ]
    """
    existing = FastPluggy.get_global("global_notification_rules") or []

    # Create a dictionary by name to avoid duplicates
    existing_by_name = {rule["name"]: rule for rule in existing}

    for rule in rules:
        name = rule.get("name")
        if name and name not in existing_by_name:
            existing_by_name[name] = rule

    # Update global rules with merged values
    FastPluggy.register_global("global_notification_rules", list(existing_by_name.values()))



def get_matching_notifier_rules(event_type: str, rules: Optional[List[dict]]) -> List[dict]:
    """
    Given an event type and a list of rules, return all matching rule dicts
    where the event_type is in rule['events'] or '*' is included.
    """
    if not rules:
        return []

    return [
        rule
        for rule in rules
        if event_matches(event_type=event_type, rule_events=rule.get("events", []))
    ]


def build_notifier_from_dict(data: dict) -> BaseNotifier:
    """
    Given a serialized notifier config dict, dynamically import and instantiate the notifier.
    """
    class_path = data.get("class")
    if not class_path:
        raise ValueError("Missing 'class' key in notifier config")

    module_path, class_name = class_path.rsplit(".", 1)

    try:
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to import {class_path}: {e}")

    config = data.get("config", {})
    events = data.get("events", [])

    # Instantiate
    notifier = cls(config=config, events=events)

    # Apply name if provided (overrides class default)
    # if 'name' in data:
    #    notifier.name = data['name']

    return notifier


def dispatch_notification(event: NotificationEvent, context: TaskContext):
    for notifier in context.notifiers or []:
        try:
            if event_matches(rule_events=notifier.events, event_type=event.event_type):
                notifier.notify(event)
        except Exception as e:
            print(f"[NOTIFIER ERROR] {notifier.name}: {e}")


def dispatch_log_line(task_id: str, record: LogRecord):
    for notifier in record.context.notifiers or []:
        if notifier.can_handle_log and event_matches(rule_events=notifier.events, event_type="logs"):
            try:
                notifier.handle_log(LogStreamEvent(task_id, record))
            except Exception as e:
                print(f"[LOG NOTIFIER ERROR] {notifier.name}: {e}")

def dispatch_context(context: TaskContext, key: str, value: Any):
    for notifier in context.notifiers or []:
        if hasattr(notifier, "on_context"):
            notifier.on_context(task_id=context.task_id, key=key, value=value)

def resolve_notifiers_for_task(context: TaskContext) -> List[BaseNotifier]:
    """
    Given a task-specific notify_config, resolve all matching notifiers
    using both global and task-specific rules. Return a list of BaseNotifier instances.
    """
    registry = get_notifier_registry()
    global_rules = get_global_notification_rules()

    combined_rules = context.notifier_config + global_rules
    seen = set()
    notifiers: List[BaseNotifier] = []

    for rule in combined_rules:
        name = rule.get("name")
        if not name or name in seen:
            continue
        seen.add(name)

        config_dict = registry.get(name)
        if config_dict:
            try:
                notifier = build_notifier_from_dict(config_dict)
                notifier.on_task_init(context.task_id)
                notifiers.append(notifier)
            except Exception as e:
                print(f"[NOTIFIER INIT ERROR] {name}: {e}")

    return notifiers


def setup_default_notifiers():
    # Register a console notifier (default name: console_notifier)
    from ..notifiers.console import ConsoleNotifier
    console = ConsoleNotifier(config={}, events=[TaskEvent.ALL])
    register_notifier(console)

    from ..notifiers.database import DBNotifier
    register_notifier(DBNotifier(session_factory=get_db))

    # Global fallback rules
    register_global_notification_rules([
        {
            "name": console.name, "events": ["*"]
        }
    ])
