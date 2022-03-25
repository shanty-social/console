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
              <v-btn>Save</v-btn>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
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
        host: null,
        traffic: null,
      },
      host,
    }
  },
}
</script>

<style scoped>

</style>
