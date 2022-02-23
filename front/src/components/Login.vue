<template>
  <v-main>
    <v-container fluid>
      <v-layout align-center justify-center>
        <v-flex xs12 sm8 md4>
          <v-form
            ref="form"
            @submit.prevent="onLogin()"
          >
            <v-card class="elevation-12">
              <v-toolbar dark color="primary">
                <v-toolbar-title>Login</v-toolbar-title>
              </v-toolbar>
              <v-card-text>
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
                >Login</v-btn>
              </v-card-actions>
            </v-card>                
          </v-form>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
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
      rules: {
        username: [
          v => (v || '').length || 'Is required'
        ],
        password: [
          v => (v || '').length || 'Is required'
        ]
      },
      error: null,
      next: next || '/settings'
    }
  },

  methods: {
    onLogin () {
      if (!this.$refs.form.validate()) return

      this.$store
        .dispatch('auth/login', this.form)
        .then(() => {
          this.$router.push(this.next)
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
