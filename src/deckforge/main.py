from dishka.integrations.fastapi import setup_dishka
from dotenv import load_dotenv
from fastapi import FastAPI

from deckforge.config import Config
from deckforge.di.setup_container import setup_container

load_dotenv()

config = Config()
container = setup_container(config=config)

app = FastAPI()

setup_dishka(app=app, container=container)
