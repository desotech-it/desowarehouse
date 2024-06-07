# Desowarehouse

<div align="center">
    <img align="center" src="https://raw.github.com/desotech-it/desowarehouse/main/logo.png" height="256" width="256" alt="Desowarehouse logo"/>
</div>

## Description

Desowarehouse is a demo application used to demonstrate how a microservice architecture can be used to create and compose a bigger application out of many smaller applications, as separate deployable units.

The application models a sample warehouse management platform with orders from users; with the possibility of letting a warehouse worker mark those orders as shipped or denied and also generate lables for those shipments.

It is made up of the following microservices:

- MySQL (for long-term storage)
- Redis (for caching hot data such as user sessions)
- API (a python application used to route requests to the backend)
- Frontend (a NodeJS app with its own webserver used to display and render content)

The contents of the database are populated ahead of time using an SQL script file that's located in `db/initdb.d` and preloads the following users:

| Username  | Password | Role |
| ------------- | ------------- | ------------- |
| g.recchia@desolabs.com  | grecchia  | User |
| c.gramegna@desolabs.com | cgramegna  | Warehouse |
| f.grimaldi@desolabs.com | fgrimaldi | Administrator |

## Docker images

- `r.deso.tech/desowarehouse/api`
- `r.deso.tech/desowarehouse/ui`

## Deployment modes

You can deploy the application using the provided `docker-compose.yaml` or the `kubernets.yaml` files.
