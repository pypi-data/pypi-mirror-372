# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import threading
from contrast.agent.assess.rules.providers.hardcoded_key import HardcodedKey
from contrast.agent.assess.rules.providers.hardcoded_password import HardcodedPassword
from contrast.utils.patch_utils import get_loaded_modules

PROVIDER_CLASSES = [HardcodedKey, HardcodedPassword]

PROVIDERS_THREAD_NAME = "ContrastProviders"


def run_providers_in_thread():
    threading.Thread(
        target=_run_providers,
        name=PROVIDERS_THREAD_NAME,
        daemon=True,
    ).start()


def _run_providers():
    """
    Providers are non-dataflow rules that analyze the contents of a module.
    """
    for module in get_loaded_modules(use_for_patching=True).values():
        for provider_cls in PROVIDER_CLASSES:
            provider = provider_cls()
            if provider.applies_to(module):
                provider.analyze(module)
