<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout justify-center>
        <v-flex xs3 sm1 md2>
          <v-card class="elevation-12">
            <v-toolbar dark color="primary">
              <v-toolbar-title>Menu</v-toolbar-title>
            </v-toolbar>
            <v-list>
              <v-list-item-group
                v-model="selected"
              >
                <v-list-item
                  v-for="(item, i) in items"
                  :key="i"
                >
                  <v-list-item-icon>
                    <v-icon v-text="item.icon"></v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title v-text="item.name"></v-list-item-title>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-chip
                      small
                      class="teal lighten-2"
                      text-color="white"
                    >{{ item.count }}</v-chip>
                  </v-list-item-action>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-flex>
        <v-flex xs8 sm3 md8 ml-4>
          <component :is="items[selected].component"/>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
import { mapGetters } from 'vuex'
import Endpoints from '@/components/Endpoints.vue'
import Hosts from '@/components/Hosts.vue'

export default {
  name: 'Settings',

  components: {
    Endpoints,
    Hosts
  },

  data () {
    return {
      selected: 0
    }
  },

  mounted () {
    this.$store.dispatch('endpoints/fetch')
    this.$store.dispatch('hosts/fetch')
  },

  computed: {
    ...mapGetters({
      endpoints: 'endpoints/count',
      hosts: 'hosts/count'
    }),

    items () {
      return [
        { icon: 'mdi-web', name: 'Endpoints', count: this.endpoints, component: Endpoints },
        { icon: 'mdi-package-variant', name: 'Hosts', count: this.hosts, component: Hosts },
      ]
    }
  }
}
</script>

<style scoped>

</style>