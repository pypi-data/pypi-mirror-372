from pathlib import Path

from kash.exec.importing import import_and_register

import_and_register(
    __package__,
    Path(__file__).parent,
    ["base", "extras", "help", "workspace"],
)
