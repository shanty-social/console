import axios from 'axios'

export default {
  namespaced: true,

  state: {
    data: null,
  },

  getters: {
    data (state) {
      return state.data
    },

    count (state) {
      return (state.data) ? state.data.length : 0
    }
  },

  mutations: {
    update (state, data) {
      state.data = data
    }
  },

  actions: {
    fetch({ state, commit }, force=false) {
      if (!force && state.data !== null) return

      axios
        .get('/api/endpoints/')
        .then((r) => {
          commit('update', r.data.objects)
        })
        .catch(console.error)
    }
  }
}
