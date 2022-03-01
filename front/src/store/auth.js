import axios from 'axios'

export default {
  namespaced: true,

  state: {
    auth: null,
    userCount: null
  },

  getters: {
    isAuthenticated (state) {
      return state.auth !== null && state.auth !== false
    },

    whoami (state) {
      return state.auth
    },

    userCount (state) {
      return state.userCount
    }
  },

  mutations: {
    updateAuth (state, user) {
      state.auth = user
      if (user) {
        this._vm.$socket.connect()
      }
    },

    updateUserCount (state, count) {
      state.userCount = count
    }
  },

  actions: {
    whoami ({ state, commit }) {
      return new Promise((resolve) => {
        if (state.auth === false) {
          resolve(null)
          return
        } else if (state.auth) {
          resolve(state.auth)
          return
        }
        axios
          .get('/api/users/whoami/')
          .then((r) => {
            commit('updateAuth', r.data)
            resolve(state.auth)
          })
          .catch(() => {
            commit('updateAuth', false)
            resolve(null)
          })
      })
    },

    fetchUserCount({ state, commit }, force=false) {
      if (!force && state.userCount !== null) return

      axios
        .get('/api/users/count/')
        .then((r) => {
          commit('updateUserCount', r.data.userCount)
        })
        .catch(console.error)
    },

    async login ({ commit, dispatch }, data) {
      const r = await axios.post('/api/users/login/', data)
      dispatch('auth/fetchUserCount', true)
      commit('updateAuth', r.data)
    },

    logout({ commit }) {
      axios
        .post('/api/users/logout/')
        .then(() => {
          commit('updateAuth', null)
        })
        .catch(console.error)
    }
  }
}
