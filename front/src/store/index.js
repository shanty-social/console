import Vue from 'vue'
import Vuex from 'vuex'
import Auth from './auth'
import Endpoints from './endpoints'
import Hosts from './hosts'
import Socket from './socket'
import Tasks from './tasks'
import Messages from './messages'
import OAuth from './oauth'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    auth: Auth,
    endpoints: Endpoints,
    hosts: Hosts,
    socket: Socket,
    tasks: Tasks,
    messages: Messages,
    oauth: OAuth,
  }
})
