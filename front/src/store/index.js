import Vue from 'vue'
import Vuex from 'vuex'
import Auth from './auth'
import Hosts from './hosts'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    auth: Auth,
    hosts: Hosts
  }
})
