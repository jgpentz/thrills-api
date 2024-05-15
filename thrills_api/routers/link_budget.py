from fastapi import APIRouter
from thrills_api.internals.link_budget import getLinkBudget
from collections import defaultdict

FREQUENCY_LIST = [58.32, 60.48, 62.64, 64.80, 66.96, 69.12]
BANDWIDTH_LIST = ["FULL", "HALF", "QUARTER", "EIGHTH", "SIXTEENTH"]
POWER_LIST = [43, 40, 36, 32]
ALT = 5000  # Altitude in meters

# Generate the route for the link budget
router = APIRouter()


def create_link_budget():
    """
    Calculates the link budget range and datarate values for each permutation
    and stores this in the link budget dict
    """
    # Create the link budget dictionary of shape
    # [frequency][bandwidth][power]
    nested_dict = lambda: defaultdict(nested_dict)
    link_budget = nested_dict()

    for ff, freq in enumerate(FREQUENCY_LIST):
        for bw in BANDWIDTH_LIST:
            for pp, pwr in enumerate(POWER_LIST):
                # Get the range and datarate arrays
                (range_km_v, _, datarate_mbps_v) = getLinkBudget(freq, ALT, pwr, bw)

                # Reverse them, put range into meters and datarate into gbps,
                # then turn them into an array
                range_km_v = range_km_v[::-1] * 1e3
                range_km_v = list(range_km_v)
                datarate_mbps_v = datarate_mbps_v[::-1] / 1e3
                datarate_mbps_v = list(datarate_mbps_v)

                # Store the data in the link budget dict
                # Data points should be an object of x,y pairs: XYPoint = {"x": int, "y": int}
                link_budget[f"ch{ff + 1}"][f"{bw.lower()}"][f"auto{pp}"] = [
                    {"x": r, "y": d} for r, d in zip(range_km_v, datarate_mbps_v)
                ]

    router.link_budget = link_budget
    return


# Return the results of the populated link_budget dict
@router.get("/link_budget", tags=["link_budget"])
async def read_link_budget():
    return router.link_budget
