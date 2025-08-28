import json
import os
from typing import Dict


def get_macro_values() -> Dict[str, str]:
    """
    Parse macro environment JSON into dict. To make this work use the icpconfigGetMacros program.

    Returns: Macro Key:Value pairs as dict
    """
    macros = json.loads(os.environ.get("MACROS", "{}"))
    macros = {key: value for (key, value) in macros.items()}
    return macros
