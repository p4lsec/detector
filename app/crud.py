import logging
from datetime import datetime
from sqlalchemy.orm import Session
from . import models

log = logging.getLogger(__name__)

def add_ip(db: Session, ip: str) -> None:
    """
    Add a new IP address to the Tor exit nodes list if it does not already exist.

    Args:
        db (Session): The database session.
        ip (str): The IP address to add.
    """
    try:
        existing_node = db.query(models.TorExitNode).filter(models.TorExitNode.ip == ip).first()
        if existing_node:
            log.info(f"IP {ip} already exists in the database")
            return

        new_node = models.TorExitNode(ip=ip, timestamp=datetime.utcnow())
        db.add(new_node)
        db.commit()
        log.info(f"Successfully added IP {ip} to the database")
    except Exception as e:
        log.exception(f"Error adding IP {ip}: {e}")
        db.rollback()

def search_ip(db: Session, ip: str) -> bool:
    """
    Search for an IP address in the Tor exit nodes list.

    Args:
        db (Session): The database session.
        ip (str): The IP address to search for.

    Returns:
        bool: True if the IP address is found, False otherwise.
    """
    try:
        result = db.query(models.TorExitNode).filter(models.TorExitNode.ip == ip).first() is not None
        log.info(f"Search result for IP {ip}: {'found' if result else 'not found'}")
        return result
    except Exception as e:
        log.exception(f"Error searching for IP {ip}: {e}")
        raise

def get_tor_exit_nodes(db: Session) -> dict:
    """
    Retrieve the full list of Tor exit nodes.

    Args:
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the list of IP addresses.
    """
    try:
        nodes = db.query(models.TorExitNode).all()
        ip_list = [node.ip for node in nodes]
        log.info(f"Retrieved {len(ip_list)} Tor exit nodes from the database")
        return {"ips": ip_list}
    except Exception as e:
        log.exception(f"Error retrieving Tor exit nodes: {e}")
        return {"ips": []}

def delete_ip(db: Session, ip: str) -> None:
    """
    Delete an IP address from the Tor exit nodes list.

    Args:
        db (Session): The database session.
        ip (str): The IP address to delete.
    """
    try:
        node = db.query(models.TorExitNode).filter(models.TorExitNode.ip == ip).first()
        if node:
            db.delete(node)
            db.commit()
            log.info(f"Successfully deleted IP {ip} from Tor exit nodes")
        else:
            log.warning(f"Attempted to delete non-existent IP {ip}")
    except Exception as e:
        log.exception(f"Error deleting IP {ip}: {e}")
        db.rollback()