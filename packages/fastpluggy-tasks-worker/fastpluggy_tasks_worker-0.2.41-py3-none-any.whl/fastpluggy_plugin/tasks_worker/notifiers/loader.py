# domains/tasks_worker/notifiers/loader.py

from fastpluggy.core.tools.inspect_tools import call_with_injection
from loguru import logger

from ..config import TasksRunnerSettings


def load_external_notification_config_from_settings():
    """
    TODO: may duplicate with build_notifier_from_dict
    Charge dynamiquement les fonctions de configuration de notificateurs
    à partir des chemins définis dans `TasksRunnerSettings.external_notification_loaders`.

    Chaque chemin doit correspondre à une fonction compatible avec call_with_injection.
    Cette fonction peut enregistrer un ou plusieurs notificateurs via `register_notifier(...)`
    ou `register_notification_rules(...)`.
    """
    settings = TasksRunnerSettings()
    path_list = settings.external_notification_loaders

    if not path_list:
        logger.info("[ℹ️] No external_notification_loaders configured.")
        return

    if isinstance(path_list, str):
        # Autorise les strings séparées par des virgules
        path_list = [p.strip() for p in path_list.split(",") if p.strip()]

    for full_path in path_list:
        try:
            logger.info(f"[🔍] Loading notifier config from: {full_path}")
            functions = call_with_injection(full_path)

            if not isinstance(functions, list):
                functions = [functions]

            for fn in functions:
                try:
                    fn()
                except Exception as e:
                    logger.info(f"[❌] Error while calling notifier config function `{fn}`: {e}")

        except Exception as e:
            logger.exception(f"[❌] Failed to resolve notification config from path `{full_path}`: {e}")
