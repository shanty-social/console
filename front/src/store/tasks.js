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
      return state.data.length
    },

    active (state) {
        return state.data.filter(o => o.completed === null)
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
        .get('/api/tasks/')
        .then((r) => {
          commit('update', r.data.objects)
        })
        .catch(console.error)
    }
  }
}
