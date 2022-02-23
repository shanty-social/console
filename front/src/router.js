import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/views/Home'
import Authentication from '@/views/Authentication'
import Settings from '@/views/Settings'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/login',
      name: 'Login',
      component: Authentication
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings
    }
  ]
})
