import { createStore } from 'vuex'
import Auth from '@/store/auth'
import Endpoints from '@/store/endpoints'
import Hosts from '@/store/hosts'
import Socket from '@/store/socket'
import Tasks from '@/store/tasks'
import Messages from '@/store/messages'
import OAuth from '@/store/oauth'

const store = createStore({
  modules: {
    auth: Auth,
    endpoints: Endpoints,
    hosts: Hosts,
    socket: Socket,
    tasks: Tasks,
    messages: Messages,
    oauth: OAuth,
  }
});

export default store;
