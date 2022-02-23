import Vue from 'vue'
import axios from 'axios'
import VueTimeago from 'vue-timeago'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'

Vue.config.productionTip = false
axios.defaults.withCredentials = true
Vue.use(VueTimeago, {
  name: 'Timeago',
  locale: 'en'
})

new Vue({
  router,
  vuetify,
  store,
  render: h => h(App)
}).$mount('#app')
