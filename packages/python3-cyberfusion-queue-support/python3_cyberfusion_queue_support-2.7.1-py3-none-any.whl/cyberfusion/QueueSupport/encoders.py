from json import JSONEncoder
from typing import Any

from cyberfusion.DatabaseSupport.database_user_grants import DatabaseUserGrant
from cyberfusion.DatabaseSupport.database_users import DatabaseUser
from cyberfusion.DatabaseSupport.databases import Database
from cyberfusion.SystemdSupport import Unit

from cyberfusion.QueueSupport.outcomes import OutcomeInterface
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.sentinels import UNKNOWN


class CustomEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, _Item):
            return {
                key: value for key, value in vars(o).items() if not key.startswith("_")
            }
        elif isinstance(o, OutcomeInterface):
            return vars(o)
        elif isinstance(o, Unit):
            return {"name": o.name}
        elif isinstance(o, Database):
            return {"name": o.name, "server_software_name": o.server_software_name}
        elif isinstance(o, DatabaseUser):
            return {
                "name": o.name,
                "server_software_name": o.server_software_name,
                "host": o.host,
            }
        elif isinstance(o, DatabaseUserGrant):
            return {
                "database": o.database,
                "database_user": o.database_user,
                "privileges_name": o.privilege_names,
                "table_name": o.table_name,
            }
        elif o == UNKNOWN:
            return "unknown"

        return super().default(o)
