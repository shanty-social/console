<template>
  <v-main>
    <Login
      v-if="userCount"
    />
    <Register
      v-else
    />
  </v-main>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import Login from '@/components/Login'
import Register from '@/components/Register'

export default {
  name: 'Authentication',

  components: {
    Login,
    Register
  },

  mounted () {
    this.fetchUserCount()
  },

  computed: {
    ...mapGetters({ userCount: 'auth/userCount' })
  },

  methods: {
    ...mapActions({ fetchUserCount: 'auth/fetchUserCount' })
  }
}
</script>

<style scoped>
</style>
