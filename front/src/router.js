import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'
import Settings from '@/views/Settings.vue'
import Endpoint from '@/views/Endpoint.vue'
import Home from '@/views/Home.vue'
import Authentication from '@/views/Authentication.vue'

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

const router = createRouter({
  history: createWebHistory(),
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
      path: '/endpoint',
      name: 'Endpoint',
      component: Endpoint,
      beforeEnter: requiresAuth
    }
  ]
});

export default router;
