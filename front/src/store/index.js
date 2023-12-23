import { createStore } from 'vuex'
import auth from '@/store/auth'
import endpoints from '@/store/endpoints'
import hosts from '@/store/hosts'
import socket from '@/store/socket'
import tasks from '@/store/tasks'
import messages from '@/store/messages'
import oauth from '@/store/oauth'
import options from '@/store/options'

const store = createStore({
  modules: {
    auth,
    endpoints,
    hosts,
    socket,
    tasks,
    messages,
    oauth,
    options,
  }
});

export default store;
