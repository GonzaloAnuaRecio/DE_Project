Data Enginering final project

Authors: Lukas Arana, Gonzalo añua, Oier Ijurko, Joanes De Miguel

How to set up

The project has a docker compose for deploying the MariaDB and Neo4J databases and a .sh running python files that do the data Cleansing, Enrichemnt and augmentation.
Therefore, these are the steps to run our project after cloning the repo.

docker compose up -d

python -m venv .venv (creating a VirtualEnv in python is recommended).
source .venv/bin/activate
pip install -r requirements.

sh main.sh
