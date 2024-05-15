from fastapi import APIRouter

from thrills_api.internals.msg_payload_types import MsgType
from thrills_api.internals.node_manager_client import node_manager_client

# Generate the route for the link budget
router = APIRouter()


# Return the results of the populated link_budget dict
@router.get("/multipath", tags=["multipath"])
async def read_map():
    multipath_data = node_manager_client(MsgType.MULTIPATH)
    return multipath_data
