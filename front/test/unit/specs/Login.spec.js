import Vue from 'vue'
import Login from '@/pages/Login'

describe('Login.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(Login)
    const vm = new Constructor().$mount()
    expect(vm.$el.querySelector('button').textContent)
    .toEqual('Login')
  })
})
