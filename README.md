# djan-go-baby-go
In less than three minutes this will set up a fully functional rapid application dev environment with Django and Vue.

Ensure you have [Docker](https://docs.docker.com/desktop/), make a copy of this template repo, then run:

```bash
./bootstrap.sh <my project name>
```

The bootstrap script will:
- Rename everything in the project from `gobabygo` to your project name.
- Populate the `.env.tmpl` into `.env` with suitable starting values.
- Builds/pulls containers from the docker-compose file.
- Generates and applies initial Django migrations.

The final step of the bootstrap script runs `docker compose up`, check http://localhost:8888/ to find a running app.

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
