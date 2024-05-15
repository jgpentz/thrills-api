from fastapi import APIRouter

from thrills_api.internals.msg_payload_types import MsgType
from thrills_api.internals.node_manager_client import node_manager_client

# Generate the route for the link budget
router = APIRouter()


# Return the results of the populated link_budget dict
@router.get("/derived_data/{sn}", tags=["derived_data"])
async def read_derived_data(sn: str):
    data = {
        "sn": sn,
    }
    dd_sn = node_manager_client(MsgType.DERIVED_DATA, data)
    return dd_sn
