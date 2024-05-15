from fastapi import APIRouter
import socket

# Generate the route for the link budget
router = APIRouter()


# Return the results of the populated link_budget dict
@router.get("/hostname", tags=["hostname"])
async def read_hostname():
    hostname = {}
    hostname["hostname"] = socket.gethostname()[:-1]
    return hostname
