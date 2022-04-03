<template>
  <v-card class="elevation-12">
    <v-toolbar dark color="primary">
      <v-toolbar-title>Endpoints</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-btn
          icon
          to="/endpoint"
        ><v-icon>mdi-plus</v-icon></v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <v-card-text>
      <p>Endpoints route traffic from the Internet to your websites.</p>
      <v-list>
        <v-list-item
          v-for="(item, i) of items"
          :key="i"
          :data="item"
        >
          <v-list-item-icon>
            <v-icon large>mdi-web</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ item.name }}</v-list-item-title>
            <v-list-item-subtitle>
              <span class="text--primary">port</span> &mdash; {{ item.port }}
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-content>
            <v-list-item-title>Domain</v-list-item-title>
            <v-list-item-subtitle>{{ item.domain_name }}</v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn
              icon
              @click="remove(item.uid)"
            ><v-icon>mdi-pencil-outline</v-icon></v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Hosts',

  mounted () {
    this.fetch(true)
  },

  computed: {
    ...mapGetters({ items: 'endpoints/data' })
  },

  methods: {
    ...mapActions({
      fetch: 'endpoints/fetch'
    })
  }
}
</script>

<style scoped>

</style>