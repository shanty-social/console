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
      host,
    }
  },

  methods: {
    save () {
      const data = {
        name: this.form.traffic,
        domain_name: this.form.traffic,
        host: this.form.host.host.name,
        port: this.form.host.port,
      }
      console.log(data)
      axios
        .post('/api/endpoints/', data)
        .then((r) => {
          console.log(r)
        })
        .catch(console.error)
    }
  }
}
</script>

<style scoped>

</style>
