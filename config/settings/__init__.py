# Default import path `config.settings` resolves to this package.
# Prefer explicit modules: config.settings.local | config.settings.production
from .local import *  # noqa: F401,F403
