<template>
  <v-main>
    <v-container fluid fill-height>
      <v-row no-gutters>
        <v-col
          cols="4"
          v-for="item, i in items"
          v-bind:key="i"
        >
          <v-card class="pa-2 ma-2">
            <v-toolbar dark color="primary"><v-toolbar-title>{{ item.name }}</v-toolbar-title></v-toolbar>
            <v-card-text>
              <HostPreview v-bind:value="item"/>
            </v-card-text>
            <v-card-actions>
              <v-btn>Launch<v-icon>mdi-play</v-icon></v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import HostPreview from '@/components/endpoint/HostPreview'

export default {
  name: 'Backends',

  components: {
    HostPreview,
  },

  data () {
    return {
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
        const { host_name, address, port, domain_name } = this.editing
        this.form.host.host.name = host_name
        this.form.host.host.addr = address
        this.form.host.port = port
        this.form.traffic = domain_name
      })
  },

  computed: {
    ...mapGetters({ items: 'hosts/data' })
  },

  methods: {
    ...mapActions({
      fetch: 'hosts/fetch',
      remove: 'backends/remove',
      save: 'backends/save',
    }),
  }
}
</script>

<style scoped>

</style>
