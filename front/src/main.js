import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { createApp } from 'vue';
import App from './App.vue';
import store from '@/store';
import router from '@/router';

import './style.css';
import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';

const vuetify = createVuetify({
    components,
    directives,
    theme: {
      defaultTheme: 'dark',
    },
});

const app = createApp(App);
app.use(vuetify);
app.use(store);
app.use(router);
app.mount('#app');
