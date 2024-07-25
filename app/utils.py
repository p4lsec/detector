import os
import logging
import requests
from typing import List

from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from . import models, database, crud

log = logging.getLogger(__name__)

TOR_LIST_URL = os.getenv("TOR_LIST_URL")

scheduler = BackgroundScheduler()

def fetch_tor_exit_nodes() -> List[str]:
    """
    Fetch the list of Tor exit nodes from the configured URL.

    Returns:
        List[str]: A list of IP addresses representing Tor exit nodes.
    """
    log.info(f"Fetching Tor exit nodes from {TOR_LIST_URL}")
    try:
        response = requests.get(TOR_LIST_URL)
        response.raise_for_status()
        exit_nodes = extract_ips(response.text)
        log.info(f"Successfully fetched {len(exit_nodes)} Tor exit nodes")
        return exit_nodes
    except requests.RequestException as e:
        log.exception(f"Failed to fetch Tor exit nodes: {e}")
        raise

def store_exit_nodes_in_db(db: Session, exit_nodes: List[str]) -> None:
    """
    Store the list of Tor exit nodes in the database.

    Args:
        db (Session): The database session.
        exit_nodes (List[str]): A list of IP addresses to be stored.
    """
    log.info(f"Storing {len(exit_nodes)} exit nodes in the database")
    try:
        db.query(models.TorExitNode).delete()
        log.info("Cleared existing nodes from the database")
        for node in exit_nodes:
            db_node = models.TorExitNode(ip=node)
            db.add(db_node)
        db.commit()
        log.info("Successfully stored new exit nodes in the database")
    except Exception as e:
        log.exception(f"Error storing exit nodes in database: {e}")
        db.rollback()

def refresh_tor_exit_nodes() -> None:
    """
    Refresh the list of Tor exit nodes by fetching new data and storing it in the database.
    """
    log.info("Starting Tor exit nodes refresh")
    db = database.SessionLocal()
    try:
        exit_nodes = fetch_tor_exit_nodes()
        store_exit_nodes_in_db(db, exit_nodes)
        log.info(f"Refreshed Tor exit nodes. Total nodes: {len(exit_nodes)}")
    except Exception as e:
        log.exception(f"Error refreshing Tor exit nodes: {e}")
        db.rollback()
    finally:
        db.close()

def extract_ips(input_string: str) -> List[str]:
    """
    Extract IP addresses from the input string, removing brackets if present.

    Args:
        input_string (str): The input string containing IP addresses.

    Returns:
        List[str]: A list of extracted IP addresses.

    Raises:
        ValueError: If the input string is empty.
    """
    log.info("Extracting IP addresses from input string")

    if not input_string:
        log.error("Input string is empty")
        raise ValueError("Input string cannot be empty")

    lines = input_string.split('\r\n')
    ip_list = [line.replace('[', '').replace(']', '').strip() for line in lines if line.strip()]

    log.info(f"Extracted {len(ip_list)} IP addresses")
    return ip_list