import api from '@/api'

export default {
  namespaced: true,

  state: {
    whoami: null,
    activated: null
  },

  getters: {
    isAuthenticated (state) {
      return state.whoami !== null
    },

    whoami (state) {
      return state.whoami
    },

    isActivated (state) {
      return state.activated
    }
  },

  mutations: {
    setWhoami (state, user) {
      state.whoami = user
      if (user) {
        this._vm.$socket.connect()
      }
    },

    setActivated (state, activated) {
      state.activated = activated
    }
  },

  actions: {
    whoami ({ state, commit }) {
      return new Promise((resolve) => {
        api
          .get('/api/users/whoami/')
          .then((r) => {
            commit('setWhoami', r.data)
            resolve(state.whoami)
          })
          .catch(() => {
            commit('setWhoami', null)
            resolve(null)
          })
      })
    },

    login({ commit }, data) {
      api
        .post('/api/users/login/', data)
        .then((r) => {
          commit('setWhoami', r.data)
        })
        .catch(console.error)
    },

    logout({ commit }) {
      api
        .post('/api/users/logout/')
        .then(() => {
          commit('setWhoami', null)
        })
        .catch(console.error)
    },

    checkActivated({ commit }) {
      api
        .get('/api/users/activated/')
        .then((r) => {
          commit('setActivated', r.data)
        })
        .catch(console.error)
    }
  }
}
