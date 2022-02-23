<template>
  <div>
    <v-btn
      v-if="!isAuthenticated"
      to="/login"
    >
      {{ (userCount) ? 'Login' : 'Register' }}
      <v-icon>mdi-login-variant</v-icon>
    </v-btn>
    <v-btn
      v-else
      @click.prevent="onLogout"
    >
      Logout
      <v-icon>mdi-logout-variant</v-icon>
    </v-btn>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Account',

  data () {
    return {
      user: null
    }
  },

  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      userCount: 'auth/userCount'
    })
  },

  methods: {
    ...mapActions({
      whoami: 'auth/whoami',
      fetchUserCount: 'auth/fetchUserCount'
    }),

    onLogout() {
      this.$store
        .dispatch('auth/logout')
        .then(() => {
          this.$router.push('/login')
        })
        .catch(console.error)
    }
  },

  mounted () {
    this.whoami()
    this.fetchUserCount()
  }
}
</script>

<style scoped>

</style>
