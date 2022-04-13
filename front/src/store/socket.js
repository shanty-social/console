export default {
  actions: {
    'socket_models.task.post_save'({ commit }, data) {
      commit('tasks/add', data)
    },

    'socket_models.task.post_delete'({ commit }, data) {
      commit('tasks/del', data.id)
    },

    'socket_models.message.post_save'({ commit }, data) {
      commit('messages/add', data)
    },
  }
}
