import logging

from datetime import datetime

from sqlalchemy.orm import Session

from . import models

log = logging.getLogger(__name__)

def add_ip(db: Session, ip: str):
    try:
        existing_node = db.query(models.TorExitNode).filter(models.TorExitNode.ip == ip).first()
        if existing_node:
            return

        new_node = models.TorExitNode(ip=ip, timestamp=datetime.utcnow())
        db.add(new_node)
        db.commit()

    except Exception:
        log.exception(f"Error adding IP {ip}")
        db.rollback()

def search_ip(db: Session, ip: str) -> bool:
    try:
        result = db.query(models.TorExitNode).filter(models.TorExitNode.ip == ip).first() is not None
        return result
    except Exception:
        log.exception(f"Error searching for IP {ip}")
        raise

def get_tor_exit_nodes(db: Session):
    try:
        nodes = db.query(models.TorExitNode).all()
        ip_list = [node.ip for node in nodes]
        return {"ips": ip_list}
    except Exception:
        return {"ips": []}

def delete_ip(db: Session, ip: str):
    try:
        node = db.query(models.TorExitNode).filter(models.TorExitNode.ip == ip).first()
        if node:
            db.delete(node)
            db.commit()
            log.info(f"Successfully deleted IP {ip} from Tor exit nodes")
        else:
            log.warning(f"Attempted to delete non-existent IP {ip}")
    except Exception:
        log.exception(f"Error deleting IP {ip}")
        db.rollback()