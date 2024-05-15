"""Main module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from thrills_api.routers import (
    channel_selection,
    derived_data,
    hostname,
    link_budget,
    link_map,
    log,
    multipath,
    radio_list,
)

ORIGINS = ["*"]


def initialize() -> FastAPI:
    # Initialize the link budget model
    link_budget.create_link_budget()

    # Create the api, add CORS origins, and set up the routes
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(link_budget.router)
    app.include_router(radio_list.router)
    app.include_router(log.router)
    app.include_router(link_map.router)
    app.include_router(multipath.router)
    app.include_router(channel_selection.router)
    app.include_router(derived_data.router)
    app.include_router(hostname.router)
    return app


app = initialize()
