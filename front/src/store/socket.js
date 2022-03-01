export default {
  actions: {
    'socket_models.task.post_save'(_, data) {
      console.log('task.created', data)
    }
  }
}
