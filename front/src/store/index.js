import Vue from 'vue'
import Vuex from 'vuex'
import Auth from './auth'
import Frontends from './frontends'
import Backends from './backends'
import Hosts from './hosts'
import Socket from './socket'
import Tasks from './tasks'
import Messages from './messages'
import OAuth from './oauth'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    auth: Auth,
    frontends: Frontends,
    backends: Backends,
    hosts: Hosts,
    socket: Socket,
    tasks: Tasks,
    messages: Messages,
    oauth: OAuth,
  }
})
