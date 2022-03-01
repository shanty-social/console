import Vue from 'vue'
import axios from 'axios'
import VueTimeago from 'vue-timeago'
import SocketIO from 'socket.io-client'
import VueSocketIO from 'vue-socket.io'
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
Vue.use(new VueSocketIO({
  debug: true,
  connection: SocketIO('ws://localhost:8080/', { autoConnect: false, transports: ['websocket'] }),
  vuex: {
    store,
    actionPrefix: 'socket_'
  }
}))

new Vue({
  router,
  vuetify,
  store,
  render: h => h(App)
}).$mount('#app')
