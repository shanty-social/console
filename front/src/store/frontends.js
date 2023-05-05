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
    },

    update(state, data) {
      const i = state.data.findIndex((o) => o.id === data.id)
      if (i !== -1) {
        state.data[i] = data
      } else {
        state.data.push(data)
      }
    },
  },

  actions: {
    fetch ({ commit }) {
      return new Promise((resolve, reject) => {
        axios
        .get('/api/frontends/')
        .then((r) => {
          commit('set', r.data.objects)
          resolve()
        })
        .catch((e) => {
          console.error(e)
          reject(e)
        })
      })
    },

    remove ({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        axios
        .delete(`/api/frontends/${id}/`)
        .then(() => {
          const data = state.data.filter((o) => o.id !== id)
          commit('set', data)
          resolve(data)
        })
        .catch((e) => {
          console.error(e)
          reject(e)
        })
      })
    },

    save({ commit }, obj) {
      const { id } = obj
      const method = (id) ? axios.put : axios.post
      let url = '/api/frontends/'
      if (id) url += `${id}/`

      return new Promise((resolve, reject) => {
        method(url, obj)
        .then((r) => {
          commit('update', r.data)
          resolve(r.data)
        })
        .catch((e) => {
          console.error(e)
          reject(e)
        })
      })
    }
  }
}
