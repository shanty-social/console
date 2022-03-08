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
  },

  mutations: {
    set (state, data) {
      state.data = data
    }
  },

  actions: {
    fetch({ commit }) {
      axios
        .get('/api/hosts/')
        .then((r) => {
          commit('set', r.data.objects)
        })
        .catch(console.error)
    }
  }
}
