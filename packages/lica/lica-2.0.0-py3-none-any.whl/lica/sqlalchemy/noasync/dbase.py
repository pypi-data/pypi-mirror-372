# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

from typing import Tuple, Any

# ---------------------
# Third party libraries
# ---------------------

import decouple
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker


def create_engine_sessionclass(env_var: str = "DATABASE_URL") -> Tuple[Engine,Any]:
	url = decouple.config(env_var)
	# 'check_same_thread' is only needed in SQLite ....
	engine = create_engine(url, connect_args={"check_same_thread": False})
	Session = sessionmaker(engine, expire_on_commit=True)
	return engine, Session

__all__ = ["create_engine_sessionclass"]
