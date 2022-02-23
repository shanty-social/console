<template>
  <v-flex>
    <p>Host names are allocated for your use. They can be subdomains of a shared domain, or a domain controlled by you.</p>
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
        <v-list-item-action>
          <v-btn
            icon
            @click="remove(item.uid)"
          ><v-icon>mdi-earth-plus</v-icon></v-btn>
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-flex>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Hosts',

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