import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/pages/Home'
import Login from '@/pages/Login'
import Endpoints from '@/pages/Endpoints'
import Domains from '@/pages/Domains'

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
