<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout justify-center>
        <v-flex xs8 sm8 md6>
          <p class="text-h4">Welcome</p>
          <p>Link with a service and then set up some endpoints.</p>

          <v-list>
            <v-list-item
              v-for="(item, i) of items"
              :key="i"
            >
              <v-list-item-icon>
                <v-icon x-large>mdi-earth</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-subtitle>{{ item.name }}</v-list-item-subtitle>
                Foobar
              </v-list-item-content>
              <v-list-item-content>
                <v-list-item-subtitle>domains</v-list-item-subtitle>
                {{ item.domains.join(', ') }}
              </v-list-item-content>
              <v-list-item-content>
                <v-list-item-subtitle>Endpoints</v-list-item-subtitle>
                <router-link
                  v-for="(endpoint, i) of item.endpoints"
                  :key="i"
                  :to="`/endpoint/?id=${endpoint.id}`"
                >{{ endpoint.name }}</router-link>
              </v-list-item-content>
              <v-list-item-action>
                <v-btn
                  :href="`/api/oauth/${item.name}/start/`"
                  v-if="!item.registered"
                >
                  Activate
                  <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </v-list>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
import axios from 'axios'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Home',

  data () {
    return {
      providers: null,
    }
  },

  mounted () {
    this.fetch()
    this.fetchEndpoints()
    this.fetchProviders()
  },

  computed: {
    ...mapGetters({
      oauth: 'oauth/data',
      endpoints: 'endpoints/data',
    }),

    items () {
      const items = []

      if (this.providers === null) {
        return items
      }

      this.providers.map(provider => {
        provider.registered = false
        if (this.oauth && this.oauth.findIndex((o) => o.name === o.name) !== -1) {
          provider.registered = true
        }
        provider.endpoints = this.endpoints
        items.push(provider)
      })

      return items
    },
  },

  methods: {
    ...mapActions({
      fetch: 'oauth/fetch',
      fetchEndpoints: 'endpoints/fetch',
    }),

    fetchProviders () {
      axios
        .get('/api/oauth/providers/')
        .then((r) => {
          this.providers = r.data.objects;
        })
        .catch(console.error)
    },
  },
}
</script>

<style scoped>

</style>