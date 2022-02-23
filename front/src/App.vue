<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <div class="d-flex align-center">
        <v-btn
          to="/"
          light
        >
          Homeland console
          <v-icon>mdi-earth</v-icon>
        </v-btn>
      </div>

      <v-spacer></v-spacer>
      <account/>
    </v-app-bar>

    <v-main>
      <router-view/>
    </v-main>

    <v-footer
      padless
      color="primary lighten-1"
    >
      <v-row
        no-gutters
        justify="center"
      >
        <v-col
          class="primary lighten-2 py-4 text-center white--text"
          cols="12"
        >{{ new Date().getFullYear() }} - <strong>Homeland.social</strong></v-col>
      </v-row>
    </v-footer>
  </v-app>
</template>

<script>
import Account from '@/components/Account'

export default {
  name: 'App',

  components: {
    Account
  }
}
</script>

<style>
</style>
