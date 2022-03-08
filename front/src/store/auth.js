import axios from 'axios'

export default {
  namespaced: true,

  state: {
    whoami: null,
    userCount: null
  },

  getters: {
    isAuthenticated (state) {
      return state.whoami !== null && state.whoami !== false
    },

    whoami (state) {
      return state.whoami
    },

    userCount (state) {
      return state.userCount
    }
  },

  mutations: {
    setWhoami (state, user) {
      state.whoami = user
      if (user) {
        this._vm.$socket.connect()
      }
    },

    setUserCount (state, count) {
      state.userCount = count
    }
  },

  actions: {
    whoami ({ state, commit }) {
      return new Promise((resolve) => {
        if (state.whoami === false) {
          resolve(null)
          return
        } else if (state.whoami) {
          resolve(state.whoami)
          return
        }
        axios
          .get('/api/whoami/')
          .then((r) => {
            commit('setWhoami', r.data)
            resolve(state.whoami)
          })
          .catch(() => {
            commit('setWhoami', false)
            resolve(null)
          })
      })
    },

    logout({ commit }) {
      axios
        .get('/api/oauth/shanty/end/')
        .then(() => {
          commit('setWhoami', null)
        })
        .catch(console.error)
    }
  }
}
