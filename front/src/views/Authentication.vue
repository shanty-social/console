<template>
  <v-main>
    <Login
      v-if="userCount"
      :next="next"
    />
    <Register
      v-else
      :next="next"
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

  data () {
    let next = this.$route.query.next
    if (next) {
      next = decodeURI(next)
    }

    return {
      next,
    }
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
