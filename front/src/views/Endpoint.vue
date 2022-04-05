<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout justify-center>
        <v-flex sm12 md6>
          <v-card class="elevation-12">
            <v-toolbar dark color="primary"><v-toolbar-title>Create new endpoint</v-toolbar-title></v-toolbar>
            <v-card-text>
              <EndpointHost
                v-model="form.host"
              />
              <SharedDomain
                v-model="form.traffic"
              />
              <v-alert
                v-if="error"
                dense outlined
                type="error"
              >{{ error }}</v-alert>
              <v-btn
                @click="save"
              >Save</v-btn>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
import axios from 'axios'
import { mapActions, mapGetters } from 'vuex'
import EndpointHost from '@/components/endpoint/Host'
import SharedDomain from '@/components/endpoint/SharedDomain.vue'

export default {
  name: 'Endpoint',

  components: {
    EndpointHost,
    SharedDomain,
  },

  data () {
    let host = this.$route.query.host
    if (host) {
      host = decodeURI(host)
    }

    return {
      form: {
        host: {
          host: {
            id: host,
            name: null,
          },
          port: null,
        },
        traffic: null,
      },
      editing: null,
      error: null,
    }
  },

  mounted () {
    this
      .fetch()
      .then(() => {
        let id = this.$route.query.id
        if (!id) {
          return
        }
        id = parseInt(id, 10)
        this.editing = this.items.find((o) => o.id === id)
        if (!this.editing) {
          return
        }
        const {host, port, domain_name} = this.editing
        this.form.host.host.id = null
        this.form.host.host.name = host
        this.form.host.port = port
        this.form.traffic = domain_name
      })
  },

  computed: {
    ...mapGetters({ items: 'endpoints/data' })
  },

  methods: {
    ...mapActions({ fetch: 'endpoints/fetch' }),

    save () {
      const data = {
        name: this.form.traffic,
        domain_name: this.form.traffic,
        host: this.form.host.host.name,
        port: this.form.host.port,
      }
      axios
        .post('/api/endpoints/', data)
        .then((r) => {
          this.error = null
          console.log(r)
        })
        .catch((e) => {
          this.error = e.response.data.error
        })
    }
  }
}
</script>

<style scoped>

</style>
