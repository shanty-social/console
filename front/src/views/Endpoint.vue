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
            </v-card-text>
            <v-card-actions>
              <v-btn
                @click="onSave"
              >
                Save
                <v-icon class="ml-2">mdi-content-save-outline</v-icon>
              </v-btn>
              <v-btn to="/">
                Cancel
                <v-icon class="ml-2">mdi-window-close</v-icon>
              </v-btn>
              <v-btn
                v-if="editing"
                color="error"
                @click="onDelete"
              >
                Delete
                <v-icon class="ml-2">mdi-delete-outline</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
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
            name: name,
            addr: null,
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
        const {host_name, address, port, domain_name} = this.editing
        this.form.host.host.name = host_name
        this.form.host.host.addr = address
        this.form.host.port = port
        this.form.traffic = domain_name
      })
  },

  computed: {
    ...mapGetters({ items: 'endpoints/data' })
  },

  methods: {
    ...mapActions({
      fetch: 'endpoints/fetch',
      remove: 'endpoints/remove',
      save: 'endpoints/save',
    }),

    onSave () {
      const data = {
        id: this.editing && this.editing.id,
        name: this.form.traffic,
        domain_name: this.form.traffic,
        host_name: this.form.host.host.name,
        addr: this.form.host.host.addr,
        port: this.form.host.port,
      }
      this.save(data)
        .then(() => {
          this.$router.push('/')
        })
        .catch((e) => {
          this.error = e.response && e.response.data.error
        })
    },

    onDelete () {
      this
        .remove(this.editing.id)
        .then(() => {
          this.$router.push('/')
        })
        .catch(console.error)
    }
  }
}
</script>

<style scoped>

</style>
