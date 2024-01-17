# djan-go-baby-go
A quick template for setting up a well-rounded rapid application development environment with Django and Vue3.

Ensure you have Docker, make a copy of this repo, then run:

```bash
./bootstrap.sh <my project name>
```

The bootstrap script will:
- Project-wide find and replace `gobabygo` to your project name. Ensure it's a valid Python module name (e.g. no hyphens).
- Fill in the .env.tmpl with suitable values.
- Build and run the containers from the docker-compose file.

At the end of the bootstrap process, you should be able to visit http://localhost:8888/ to find a running app.

### What this includes

This is an opinionated template that brings together a number of other tools and libraries I've enjoyed working with. Maybe you'll like them as well.

#### Foundation & Tooling
- PostgreSQL
- Redis
- Docker Compose
- Webpack

#### Python Libraries
- Django with Jinja2
- Django Ninja
- Celery (with Beat)
- pytest

#### Frontend
- Vue 3
- Pinia
- PrimeVue component library

#### Services
- Sentry
- Stripe
