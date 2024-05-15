from fastapi import APIRouter

from thrills_api.internals.msg_payload_types import MsgType
from thrills_api.internals.node_manager_client import node_manager_client

# Generate the route for the link budget
router = APIRouter()


# Return the results of the populated link_budget dict
@router.get("/log", tags=["log"])
async def read_log():
    log = node_manager_client(MsgType.LOG)
    return log
