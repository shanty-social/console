<template>
  <v-main>
    <Login
      v-if="isActivated"
    />
    <Register
      v-else
    />
  </v-main>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import Login from '@/components/Login.vue'
import Register from '@/components/Register.vue'

export default {
  name: 'Authentication',

  components: {
    Login,
    Register
  },

  mounted () {
    this.checkActivated()
  },

  computed: {
    ...mapGetters({ isActivated: 'auth/isActivated' })
  },

  methods: {
    ...mapActions({ checkActivated: 'auth/checkActivated' })
  }
}
</script>

<style scoped>
</style>