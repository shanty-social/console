<template>
  <v-card class="elevation-12">
    <v-toolbar dark color="primary">
      <v-toolbar-title>Endpoints</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      <p>Below are the containers that you can expose to the world.</p>
      <v-list>
        <v-list-item
          v-for="(item, i) of items"
          :key="i"
          :data="item"
        >
          <v-list-item-icon>
            <v-icon large>mdi-package-variant</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ item.hostname }}</v-list-item-title>
            <v-list-item-subtitle>
              <span class="text--primary">Created</span> &mdash; <timeago :datetime="item.created"/>
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-content>
            <v-list-item-title>Image</v-list-item-title>
            <v-list-item-subtitle>{{ item.image }}</v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-content>
            <v-list-item-title>Aliases</v-list-item-title>
            <v-list-item-subtitle>{{ item.aliases.join(', ') }}</v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn
              icon
              :to="`/endpoint?host=${item.id}`"
            ><v-icon>mdi-web-plus</v-icon></v-btn>
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
    ...mapGetters({ items: 'hosts/data' })
  },

  methods: {
    ...mapActions({
      fetch: 'hosts/fetch'
    })
  }
}
</script>

<style scoped>

</style>