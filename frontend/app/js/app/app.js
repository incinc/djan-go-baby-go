import * as Sentry from "@sentry/browser";

const ENVIRONMENT = document
  .querySelector('meta[name="ENVIRONMENT"]')
  .getAttribute("value");

if (ENVIRONMENT !== "dev") {
  Sentry.init({
    dsn: document
      .querySelector('meta[name="SENTRY_DSN"]')
      .getAttribute("value"),
    environment: ENVIRONMENT,
  });
}

import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";

import PrimeVue from "primevue/config";

import AppRoot from "@app/components/AppRoot.vue";
import Test from "@app/components/Test.vue";

import "primeflex/primeflex.css";
import "@fontsource-variable/inter";
import "primeicons/primeicons.css";
import "@frontend/app/css/base.css";

const pinia = createPinia();

const routes = [{ path: "/vue/test", component: Test }];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const app = createApp(AppRoot);
app.use(PrimeVue, {
  // Default theme configuration
  theme: {
    preset: Aura,
    options: {
      prefix: "",
      darkModeSelector: "system",
      cssLayer: false,
    },
  },
});
app.use(pinia);
app.use(router);

app.mount("#vue-router-base");
