import axios from 'axios'

export default {
  namespaced: true,

  state: {
    data: [],
  },

  getters: {
    data (state) {
      return state.data
    },

    count (state) {
      return state.data ? state.data.length : 0
    }
  },

  mutations: {
    set (state, data) {
      state.data = data
    }
  },

  actions: {
    fetch({ commit }) {
      return new Promise((resolve, reject) => {
        axios
          .get('/api/hosts/')
          .then((r) => {
            commit('set', r.data.objects)
            resolve()
          })
          .catch((e) => {
            console.error(e)
            reject(e)
          })
      })
    }
  }
}
