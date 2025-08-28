from .output import fatal as fatal
from .output import print_json as json
from .output import print_plain as plain
from .output import print_table as table
from .output import print_toml as toml

__all__ = ["fatal", "json", "plain", "table", "toml"]
