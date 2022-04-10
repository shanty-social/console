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
    },

    add (state, data) {
      const index = state.data.findIndex(o => o.id === data.id)
      if (index !== -1) {
        state.data.splice(index, 1)
      }
      state.data.push(data)
    },

    del (state, id) {
      const index = state.data.findIndex(o => o.id === id)
      state.data.splice(index, 1)
    },
  },

  actions: {
    fetch({ commit }) {
      axios
        .get('/api/tasks/')
        .then((r) => {
          commit('set', r.data.objects)
        })
        .catch(console.error)
    },

    delete ({ commit }, id) {
      axios
        .delete(`/api/tasks/${id}/`)
        .then(() => {
          commit('del', id)
        })
        .catch((e) => {
          if (e.response && e.response.status === 404) {
            commit('del', id)
          }
          console.error(e)
        })
    },

    clear ({ commit }) {
      axios
        .delete('/api/tasks/')
        .then(() => {
          commit('set', [])
        })
        .catch(console.error)
    },
  }
}
