<template>
  <v-main>
    <v-container fluid>
      <v-layout align-center justify-center>
        <v-flex xs12 sm8 md4>
          <v-form
            ref="form"
            @submit.prevent="onRegister()"
          >
            <v-card class="elevation-12">
              <v-toolbar dark color="primary">
                <v-toolbar-title>Register</v-toolbar-title>
              </v-toolbar>
              <v-card-text>
                <v-text-field
                  v-model="form.name"
                  name="name"
                  label="Name"
                  type="text"
                  placeholder="name"
                  :rules="rules.name"
                ></v-text-field>    
                <v-text-field
                  v-model="form.username"
                  name="username"
                  label="Username"
                  type="text"
                  placeholder="username"
                  :rules="rules.username"
                ></v-text-field>    
                <v-text-field
                  v-model="form.password"
                  name="password"
                  label="Password"
                  type="password"
                  placeholder="password"
                  :rules="rules.password"
                ></v-text-field>
                <v-alert
                  v-if="error"
                  dense outlined
                  type="error"
                >{{ error }}</v-alert>
              </v-card-text>
              <v-card-actions>
                <v-btn
                  type="submit" color="primary" value="log in"
                >Register</v-btn>
              </v-card-actions>
            </v-card>                
          </v-form>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>

</template>

<script>
import axios from 'axios'
import { mapActions } from 'vuex'

export default {
  name: 'Register',

  data () {
    let next = this.$route.query.next
    if (next) {
      next = decodeURI(next)
    }

    return {
      form: {
        name: null,
        username: null,
        password: null
      },
      rules: {
        name: [
          v => (v || '').length || 'Is required'
        ],
        username: [
          v => (v || '').length || 'Is required'
        ],
        password: [
          v => (v || '').length || 'Is required'
        ]
      },
      error: null,
      next: next || '/'
    }
  },

  methods: {
    ...mapActions({ checkActivated: 'auth/checkActivated' }),

    onRegister () {
      if (!this.$refs.form.validate()) return

      axios
        .post('/api/users/', this.form)
        .then(() => {
          this.checkActivated(true)
        })
        .catch((e) => {
          this.error = e.message
        })
    }
  }
}
</script>

<style scoped>

</style>