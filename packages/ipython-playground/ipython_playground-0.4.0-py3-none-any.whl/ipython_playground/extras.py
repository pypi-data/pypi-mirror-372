# ruff: noqa: F401

import inspect
import pkgutil
import sys
from types import ModuleType
from typing import Optional

from .utils import log


def load_app_modules() -> dict:
    """Attempt to import common app modules and return them in a dict."""
    modules = {}
    try:
        import app.models

        modules["app.models"] = app.models
    except ImportError:
        log.warning("Could not import app.models")

    try:
        import app.commands

        modules["app.commands"] = app.commands
    except ImportError:
        log.warning("Could not import app.commands")

    try:
        import app.jobs

        modules["app.jobs"] = app.jobs
    except ImportError:
        log.warning("Could not import app.jobs")

    return modules


def load_modules_for_ipython() -> dict:
    """Load list of common modules for use in ipython sessions and return them as a dict so they can be appended to the global namespace"""

    modules = {}

    # Load app modules
    modules.update(load_app_modules())

    try:
        import funcy_pipe as fp

        modules["fp"] = fp
    except ImportError:
        log.warning("Could not import funcy_pipe")

    try:
        import sqlalchemy as sa

        modules["sa"] = sa
    except ImportError:
        log.warning("Could not import sqlalchemy")

    try:
        import sqlmodel as sm
        from sqlmodel import SQLModel, select

        modules["sm"] = sm
        modules["SQLModel"] = SQLModel
        modules["select"] = select
    except ImportError:
        log.warning("Could not import sqlmodel")

    return modules


def find_all_sqlmodels(module: ModuleType):
    """Import all model classes from module and submodules into current namespace."""

    try:
        from sqlmodel import SQLModel
    except ImportError:
        log.warning("Could not find SQLModel, skipping model discovery")
        return {}

    log.debug(f"Starting model import from module: {module.__name__}")
    model_classes = {}

    # Walk through all submodules
    for loader, module_name, is_pkg in pkgutil.walk_packages(module.__path__):
        full_name = f"{module.__name__}.{module_name}"
        log.debug(f"Importing submodule: {full_name}")

        # Check if module is already imported
        if full_name in sys.modules:
            submodule = sys.modules[full_name]
        else:
            log.warning(f"Module not found in sys.modules, not importing: {full_name}")
            continue

        # Get all classes from module
        for name, obj in inspect.getmembers(submodule):
            if inspect.isclass(obj) and issubclass(obj, SQLModel) and obj != SQLModel:
                log.debug(f"Found model class: {name}")
                model_classes[name] = obj

    log.debug(f"Completed model import. Found {len(model_classes)} models")
    return model_classes


def all(*, database_url: Optional[str] = None):
    from .database import get_database_url, setup_database_session
    from .redis import setup_redis

    modules = load_modules_for_ipython()

    if "app.models" in modules:
        modules = modules | find_all_sqlmodels(modules["app.models"])

    if not database_url:
        database_url = get_database_url()

    if database_url:
        modules = modules | setup_database_session(database_url)

    # Add redis client if available
    modules = modules | setup_redis()

    return modules
