import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/views/Home'
import Settings from '@/views/Settings'
import Endpoint from '@/views/Endpoint'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings
    },
    {
      path: '/endpoint',
      name: 'Endpoint',
      component: Endpoint
    }
  ]
})
