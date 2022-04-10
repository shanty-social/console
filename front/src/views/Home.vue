<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout justify-center>
        <v-flex xs8 sm8 md6>
          <p class="text-h4">Welcome</p>
          <p>Link an online service and then set up an endpoint.</p>
          <p>Each online service acts like a reverse VPN, connecting internet users to your website.</p>
          <p>Endpoints link a specific domain name to your chosen container.</p>
          <v-list>
            <v-list-item
              v-for="(item, i) of items"
              :key="i"
            >
              <v-list-item-icon>
                <v-icon x-large>mdi-cloud-outline</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-subtitle>
                  <a target="new" :href="item.url">{{ item.name }}</a>
                </v-list-item-subtitle>
                {{ item.description }}
              </v-list-item-content>
              <v-list-item-content>
                <v-list-item-subtitle>Available domains</v-list-item-subtitle>
                <a
                  v-for="domain of item.domains"
                  :key="domain"
                  target="new"
                  :href="`https://www.${domain}`"
                >{{domain}}</a>
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
                  v-if="!item.registered"
                  :href="`/api/oauth/${item.name}/start/`"
                >
                  Activate
                  <v-icon class="ml-2">mdi-chevron-right</v-icon>
                </v-btn>
                <v-btn
                  v-else
                  to="/endpoint"
                >
                  Add Endpoint
                  <v-icon class="ml-2">mdi-earth-plus</v-icon>
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