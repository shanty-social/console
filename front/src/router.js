import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/views/Home'
import Login from '@/views/Login'
import Endpoints from '@/views/Endpoints'
import Domains from '@/views/Domains'

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
      component: Login
    },
    {
      path: '/endpoints',
      name: 'Endpoints',
      component: Endpoints
    },
    {
      path: '/domains',
      name: 'Domains',
      component: Domains
    }
  ]
})
