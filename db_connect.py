import yaml
from fastapi import Depends
from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Load database config from YAML
def load_db_config(config_file='config.yaml'):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config['database']

# Create database engine from config
def get_engine_from_config(config):
    db_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['name']}"
    engine = create_engine(db_url)  # Set echo=False to disable SQL logs
    return engine

db_config = load_db_config()
engine = get_engine_from_config(db_config)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("yes")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
print("Connected to the database successfully.")
