# take-over

A simple web-app to monitor test coverage of your projects. 

It is my freetime project I develop mostly for myself and it is strongly WIP. As a MVP I
try to achieve a barebones API to store coverage reports and get badges with a simple
authentification. I am also interested in creating a full-fledged web-interface to
visualize code coverage history, download reports etc, but it is not my main priority.

## Configuration

Following environmental variables must be defined in a local `.env` file:
- `TO_DB_USERNAME`, `TO_DB_PASSWORD` - MongoDB credentials.
- `TO_JWT_KEY` - a secret key to sign JWT access tokens (see [here](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#handle-jwt-tokens)).

## Usage

**take-over** is intended to be used in a Docker container: 
```bash
docker-compose up --build -d
```

In development it is more convinient to run the service itself manually: 
```bash
export $(grep -v '^#' .env | xargs)
docker-compose up --build -d mongodb 
uvicorn app.main:app --reload
```

## Alternatives

Here are some other tools and services that also might fit your needs:
- [coveralls.io](https://coveralls.io/)
- [ccguard](https://github.com/nilleb/ccguard/)
