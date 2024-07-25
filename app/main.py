import os
import logging
import time

from typing import Generator

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from . import models, crud, schemas, database, utils

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="DetecTor API")

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

# Background task scheduler
utils.scheduler.add_job(utils.refresh_tor_exit_nodes, 'interval', hours=int(os.getenv('REFRESH_INTERVAL', 24)))
utils.scheduler.start()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get the database session.
    
    Yields:
        Generator[Session, None, None]: The database session.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event() -> None:
    """
    Event handler for application startup.
    """
    log.info("Starting up the DetecTor API")
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            engine = create_engine(os.getenv("DATABASE_URL"))
            engine.connect()
            log.info("Successfully connected to the database")
            break
        except OperationalError:
            if attempt < max_retries - 1:
                log.warning(f"Database connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                log.error("Failed to connect to the database after multiple attempts")
                raise

    # Perform initial Tor exit nodes refresh
    log.info("Performing initial Tor exit nodes refresh")
    utils.refresh_tor_exit_nodes()
    log.info("Initial Tor exit nodes refresh completed")

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Event handler for application shutdown.
    """
    log.info("Shutting down the DetecTor API")
    utils.scheduler.shutdown()
    log.info("Background scheduler shut down")

@app.get("/search", response_model=bool)
async def search_ip(ip: str, db: Session = Depends(get_db)) -> bool:
    """
    Search for an IP address to determine if it is a Tor exit node.
    
    Args:
        ip (str): The IP address to search.
        db (Session): The database session.

    Returns:
        bool: True if the IP is a Tor exit node, False otherwise.
    """
    log.info(f"Searching for IP: {ip}")
    try:
        result = crud.search_ip(db, ip)
        log.info(f"Search result for IP {ip}: {'found' if result else 'not found'}")
        return result
    except Exception as e:
        log.error(f"Error occurred while searching for IP {ip}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/list", response_model=schemas.IPList)
async def get_tor_exit_nodes(db: Session = Depends(get_db)) -> schemas.IPList:
    """
    Retrieve the full list of Tor exit nodes.
    
    Args:
        db (Session): The database session.

    Returns:
        schemas.IPList: The list of Tor exit nodes.
    """
    log.info("Retrieving list of Tor exit nodes")
    try:
        result = crud.get_tor_exit_nodes(db)
        log.info(f"Retrieved {len(result['ips'])} Tor exit nodes")
        return result
    except Exception as e:
        log.error(f"Error occurred while retrieving Tor exit nodes: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/delete")
async def delete_ip(ip: str, db: Session = Depends(get_db)) -> dict:
    """
    Delete an IP address from the list of Tor exit nodes.
    
    Args:
        ip (str): The IP address to delete.
        db (Session): The database session.

    Returns:
        dict: A message indicating the result of the deletion.
    """
    log.info(f"Attempting to delete IP: {ip}")
    try:
        crud.delete_ip(db, ip)
        log.info(f"IP {ip} deleted from the list")
        return {"message": f"IP {ip} deleted from the list"}
    except Exception as e:
        log.error(f"Error occurred while deleting IP {ip}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint to verify the API status.

    Returns:
        dict: The health status of the API.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    log.info("DetecTor API is ready to start")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)