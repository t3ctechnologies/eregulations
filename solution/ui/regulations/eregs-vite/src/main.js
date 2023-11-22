import { createApp } from "vue";
import { isNavigationFailure, NavigationFailureType } from 'vue-router'
//import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/lib/styles/main.sass'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/lib/components/index.mjs'
import * as directives from 'vuetify/lib/directives/index.mjs'

import App from "./App.vue";
import vueRouter from "./router";

import Clickaway from "./directives/clickaway";



const mountEl = document.querySelector("#vite-app");
const { customUrl, host } = mountEl.dataset;

const app = createApp(App, { ...mountEl.dataset });
const vuetifyApp = createVuetify({
    theme: {
        themes: {
            light: {
                primary: "#046791",
            },
        },
    },
});
app.use(vuetifyApp);

//Vue.directive("clickaway", Clickaway);

const router = vueRouter({ customUrl, host });

// Silence duplicate navigation errors
// see:
// - https://stackoverflow.com/questions/57837758/navigationduplicated-navigating-to-current-location-search-is-not-allowed
// - https://github.com/vuejs/vue-router/issues/2872
const originalPush = router.push;
router.push = function push(location, onResolve, onReject) {
    if (onResolve || onReject) {
        return originalPush.call(this, location, onResolve, onReject);
    }

    return originalPush.call(this, location).catch((err) => {
        if (isNavigationFailure(err, NavigationFailureType.duplicated)) {
            return err;
        }

        return Promise.reject(err);
    });
};

app.use(router);
app.mount("#vite-app");
