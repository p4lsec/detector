import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
import time

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

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
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
async def shutdown_event():
    log.info("Shutting down the DetecTor API")
    utils.scheduler.shutdown()
    log.info("Background scheduler shut down")

@app.get("/search", response_model=bool)
async def search_ip(ip: str, db: Session = Depends(get_db)):
    log.info(f"Searching for IP: {ip}")
    try:
        result = crud.search_ip(db, ip)
        log.info(f"Search result for IP {ip}: {'found' if result else 'not found'}")
        return result
    except Exception as e:
        log.error(f"Error occurred while searching for IP {ip}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/list", response_model=schemas.IPList)
async def get_tor_exit_nodes(db: Session = Depends(get_db)):
    log.info("Retrieving list of Tor exit nodes")
    try:
        result = crud.get_tor_exit_nodes(db)
        log.info(f"Retrieved {len(result['ips'])} Tor exit nodes")
        return result
    except Exception as e:
        log.error(f"Error occurred while retrieving Tor exit nodes: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/delete")
async def delete_ip(ip: str, db: Session = Depends(get_db)):
    log.info(f"Attempting to delete IP: {ip}")
    try:
        crud.delete_ip(db, ip)
        log.info(f"IP {ip} deleted from the list")
        return {"message": f"IP {ip} deleted from the list"}
    except Exception as e:
        log.error(f"Error occurred while deleting IP {ip}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    log.info("DetecTor API is ready to start")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)