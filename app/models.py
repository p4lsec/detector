from sqlalchemy import Column, String, DateTime
from .database import Base
from datetime import datetime
import pytz

class TorExitNode(Base):
    __tablename__ = "tor_exit_nodes"
    ip = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now(pytz.utc))