import Vue from 'vue'
import Router from 'vue-router'
import store from '@/store'
import Settings from '@/views/Settings'
import Frontends from '@/views/Frontends'
import Backends from '@/views/Backends'
import Home from '@/views/Home'
import Authentication from '@/views/Authentication'

Vue.use(Router)

function requiresAuth (to, from, next) {
  store
    .dispatch('auth/whoami')
    .then((r) => {
      if (r) {
        next()
      } else {
        next({
          path: '/authentication',
          query: {
            next: encodeURI(to.fullPath)
          }
        })
      }
    })
    .catch(console.error)
}

export default new Router({
  routes: [
    {
      path: '/authentication',
      name: 'Authentication',
      component: Authentication
    },
    {
      path: '/',
      name: 'Home',
      component: Home,
      beforeEnter: requiresAuth
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings,
      beforeEnter: requiresAuth
    },
    {
      path: '/frontends',
      name: 'Frontends',
      component: Frontends,
      beforeEnter: requiresAuth
    },
    {
      path: '/backends',
      name: 'Backends',
      component: Backends,
      beforeEnter: requiresAuth
    }
  ]
})
