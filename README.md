# Crew DB

A membership management system, written in Python with the [Tornado web-framework](https://www.tornadoweb.org/en/stable/) and [ORY](https://www.ory.sh/) as the authentication and identification handler.

## Installation

This project uses [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/). Every docker image in use can be found in the `docker-compose.yml` file. To build the `crew-db` docker image use the command: `docker build . --no-cache -t crew-db:latest`. This will update all the python dependencies to their latest versions. To run the project, simply run: `docker-compose up`.

## Design goals

- Clean database design
- Plugin/Module based system
- Mobile friendly
- Easy to use

## License

Crew DB is licensed under the MIT License. For more information, see the file LICENSE.