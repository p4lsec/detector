import os
import logging
import requests

from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from . import models, database, crud

log = logging.getLogger(__name__)

TOR_LIST_URL = os.getenv("TOR_LIST_URL")

scheduler = BackgroundScheduler()

def fetch_tor_exit_nodes():
    log.info(f"Fetching Tor exit nodes from {TOR_LIST_URL}")
    try:
        response = requests.get(TOR_LIST_URL)
        response.raise_for_status()
        exit_nodes = extract_ips(response.text)
        log.info(f"Successfully fetched {len(exit_nodes)} Tor exit nodes")
    
        return exit_nodes
    
    except requests.RequestException:
        log.exception(f"Failed to fetch Tor exit nodes: {response.text}")
        raise

def store_exit_nodes_in_db(db: Session, exit_nodes: list):
    log.info(f"Storing {len(exit_nodes)} exit nodes in the database")
    try:
        db.query(models.TorExitNode).delete()
        log.info("Cleared existing nodes from the database")
        for node in exit_nodes:
            db_node = models.TorExitNode(ip=node)
            db.add(db_node)
        db.commit()
        log.info("Successfully stored new exit nodes in the database")
    except Exception:
        log.exception("Error storing exit nodes in database")
        db.rollback()

def refresh_tor_exit_nodes():
    log.info("Starting Tor exit nodes refresh")
    db = database.SessionLocal()
    try:
        exit_nodes = fetch_tor_exit_nodes()
        
        # Clear existing nodes
        db.query(models.TorExitNode).delete()
        log.info("Cleared existing nodes from the database")
        
        # Add new nodes
        for node in exit_nodes:
            crud.add_ip(db, node)
        
        db.commit()
        log.info(f"Refreshed Tor exit nodes. Total nodes: {len(exit_nodes)}")
    except Exception:
        log.exception("Error refreshing Tor exit nodes")
        db.rollback()
    finally:
        db.close()

def extract_ips(input_string: str) -> list:
    """
    Extract IP addresses from the input string, removing brackets if present. Returns a list of IPs.
    """
    log = logging.getLogger(__name__)

    if not input_string:
        log.error("Input string is empty")
        raise ValueError("Input string cannot be empty")

    lines = input_string.split('\r\n')

    ip_list = []

    for line in lines:
        ip = line.replace('[', '').replace(']', '').strip()
        if ip:
            ip_list.append(ip)

    log.info(f"Extracted {len(ip_list)} IP addresses")
    return ip_list