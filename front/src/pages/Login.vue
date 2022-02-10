<template>
  <form
    v-on:submit.prevent="onLogin"
  >
    <label for="username">Username</label>
    <input
      v-model="form.username"
      type="text"
      name="username"
      placeholder="admin"
    />
    <br/>
    <label for="password">Password</label>
    <input
      v-model="form.password"
      type="password"
      name="password"
    />
    <br/>
    <button>Login</button>
    <br/>
    <p
      v-for="(error, i) in errors"
      v-bind:key="i"
      class="error"
    >{{ error }}</p>
  </form>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',

  data () {
    let next = this.$route.query.next
    if (next) {
      next = decodeURI(next)
    }

    return {
      form: {
        username: null,
        password: null
      },
      errors: [],
      next: next || '/'
    }
  },

  methods: {
    onLogin () {
      axios
        .post('/api/users/login/', this.form)
        .then((r) => {
          this.$router.push(this.next)
        })
        .catch((e) => {
          this.errors.push(e.message)
        })
    }
  }
}
</script>

<style scoped>
.error {
  color: red;
}
</style>
