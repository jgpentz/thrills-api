from fastapi import APIRouter
from pydantic import BaseModel

from thrills_api.internals.msg_payload_types import MsgType
from thrills_api.internals.node_manager_client import node_manager_client

# Generate the route for the link budget
router = APIRouter()


class ChannelSelections(BaseModel):
    bandwidth: str
    channel: str
    power: str
    beacon_mode: str


# Return the results of the populated link_budget dict
@router.post("/channel_selections/", tags=["channel_selections"])
async def update_channels(channel_selections: ChannelSelections):
    data = {
        "bandwidth": channel_selections.bandwidth,
        "channel": channel_selections.channel,
        "power": channel_selections.power,
    }
    response = node_manager_client(MsgType.CHANNEL_SELECTION, data)
    return response
