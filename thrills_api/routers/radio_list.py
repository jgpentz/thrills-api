from fastapi import APIRouter

from thrills_api.internals.msg_payload_types import MsgType
from thrills_api.internals.node_manager_client import node_manager_client

# Generate the route for the link budget
router = APIRouter()


# Return the results of the populated link_budget dict
@router.get("/radio_list", tags=["radio_list"])
async def read_radio_list():
    radio_list = node_manager_client(MsgType.RADIO_LIST)
    return radio_list
