import os
from lavoro_library.database import Database

db = Database(os.environ["DB_CONNECTION_STRING"])
