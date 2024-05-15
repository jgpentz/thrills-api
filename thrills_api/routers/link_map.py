from fastapi import APIRouter

from thrills_api.internals.msg_payload_types import MsgType
from thrills_api.internals.node_manager_client import node_manager_client

# Generate the route for the link budget
router = APIRouter()


# Return the results of the populated link_budget dict
@router.get("/link_map", tags=["link_map"])
async def read_map():
    link_map_data = node_manager_client(MsgType.LINK_MAP)
    return link_map_data
