# djan-go-baby-go
In less than three minutes this will set up a fully functional rapid application dev environment with Django and Vue.

The only requirement is [Docker](https://docs.docker.com/desktop/). Make a copy of this template repo, then run:

```bash
./bootstrap.sh <my project name>
```

The bootstrap script will:
- Rename everything in the project from `gobabygo` to your project name.
- Populate the `.env.tmpl` into `.env` with suitable starting values.
- Builds/pulls containers from the docker-compose file.
- Generates and applies initial Django migrations.

The final step of the bootstrap script runs `docker compose up`, check http://localhost:8888/ to find a running app.

The bootstrap process has been tested on Linux and MacOS, but not Windows (contributions welcome if it does not work in WSL).

### What this includes

This is an opinionated template that brings together a number of other tools and libraries I've enjoyed working with. Maybe you'll like them as well.

#### Foundation & Tooling
- [PostgreSQL](https://www.postgresql.org/docs/15/index.html)
- [Redis](https://redis.io/docs/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Webpack](https://webpack.js.org/concepts/)

#### Python Libraries
- [Django](https://docs.djangoproject.com/en/4.2/) with [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/)
- [Django Ninja](https://django-ninja.dev/)
- [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html) (with [Beat](https://django-celery-beat.readthedocs.io/en/latest/))
- [pytest](https://docs.pytest.org/en/7.4.x/)

#### Frontend
- [Vue 3](https://vuejs.org/guide/introduction.html)
  - [Vue Router](https://router.vuejs.org/guide/)
  - [Pinia](https://pinia.vuejs.org/core-concepts/)
- [PrimeVue](https://primevue.org/introduction/) component library

#### Services
- [Sentry](https://docs.sentry.io/platforms/python/integrations/django/)
- [Stripe](https://stripe.com/docs/api?lang=python)

### Contributing

The goals of the template are that it remain:

- One-click to a running app
- "Available in any color, so long as it is black"
- Easy to maintain up-to-date dependencies
- Easy to understand the structure and layout

The intent of this template is to provide a starting point where things "just work" out of the box. Contributions should follow that as a guiding principle: if a change introduces something that requires extensive customization after running the boostrap script for it to work at all, it's probably not a great thing to include.

Secondary to that, the bootstrap script is intended to be a single path: it is not the intent to introduce an interactive or configurable process that produces a different result based on user choices, but instead produce one output that can be modified manually after the fact.

Dependencies *do not follow LTS releases*. The intent is that dependencies, including Django itself, are up to date with the latest stable release wherever possible. If an important dependency becomes unmaintained or there are significant benefits to be had from an alternative, it should be replaced.
