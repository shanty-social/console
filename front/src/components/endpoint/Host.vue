<template>
  <v-form
    @submit.prevent="onCreate"
    ref="form"
  >
    <p>First we need a service to expose. You must select a host from the list of running containers.</p>
    <v-select
      v-model="form.host"
      :items="hostItems"
      item-text="name"
      item-value="id"
      :rules="rules.host"
      placeholder="choose host"
      @change="scan.results = []"
    ></v-select>
    <div
      v-if="form.host"
    >
      <p>
      Select the http service port.
      Port not listed?
      <a
        @click="onScan"
      >Scan for open ports...</a>
      </p>
      <v-radio-group
        v-model="form.port"
        :rules="rules.port"
      >
      <v-fade-transition>
        <v-radio
          v-for="n in Object.keys(portItems)"
          :key="n"
          :value="n"
        >
        <template v-slot:label>
          {{ `Port ${n}` }}
          &nbsp;
          <v-icon
          v-if="portItems[n]"
          color="green"
          >mdi-check</v-icon>
        </template>
        </v-radio>
      </v-fade-transition>
      <v-radio
        key="other"
        label="Other"
        value="other"
      />
      </v-radio-group>
      <v-text-field
        v-if="form.port === 'other'"
        v-model="form.other"
        :rules="rules.other"
        placeholder="port number"
        type="number"
      >Port</v-text-field>
    </div>
    <v-alert
      v-if="error"
      dense outlined
      type="error"
    >{{ error }}</v-alert>
    <v-btn type="submit">
      Next
      <v-icon>mdi-menu-right</v-icon>
    </v-btn>
    <v-progress-linear
      :active="scan.scanning"
      class="mt-4"
      indeterminate
    ></v-progress-linear>
  </v-form>
</template>

<script>
import axios from 'axios'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Host',

  props: {
    data: {
      type: Object,
      default: null
    }
  },

  data () {
    let host = this.$route.query.host
    if (host) {
      host = decodeURI(host)
    }

    return {
      form: {
        host,
        port: null,
        other: null
      },
      rules: {
        host: [
          v => (v || '').length > 0 || 'Is required'
        ],
        port: [
          v => (v > 0 || v === 'other') || 'Choose a port'
        ],
        other: [
          v => this.form.port !== 'other' || (v || '').length > 0 || 'Enter a port number'
        ]
      },
      error: null,
      scan: {
        scanning: false,
        results: []
      }
    }
  },

  mounted () {
    this.fetchHosts()
  },

  computed: {
    ...mapGetters({ hosts: 'hosts/data' }),

    hostItems () {
      if (!this.hosts) return
      return this.hosts.map(o => {
        return {
          id: o.id,
          name: `${o.hostname} - ${o.image}`
        }
      });
    },

    portItems () {
      const ports = {}
      this.scan.results.forEach(port => {
        ports[port] = true
      })
      if (this.form.host) {
        const host = this.hosts.find(o => o.id === this.form.host)
        host.ports.forEach(port => {
          port = parseInt(port, 10)
          if (!ports[port]) ports[port] = false
        })
      }

      return ports
    },
  },

  methods: {
    ...mapActions({ fetchHosts: 'hosts/fetch' }),

    async onCreate () {
      this.error = null

      let valid = this.$refs.form.validate()

      if (valid) {
        const host = this.hosts.find(o => o.id === this.form.host)
        const port = this.form.port !== 'other' && this.form.port || parseInt(this.form.other, 10);

        if (!this.scan.results.length || !this.scan.results.includes(port)) {
          const r = await this.portScan(host.addresses[0], port)
          if (!r.ports[port] || !r.ports[port] === 'open') {
            this.error = 'Host is unreachable'
            valid = false
          }
        }
      }

      this.$emit('status', valid);
    },

    async onScan() {
      const host = this.hosts.find(o => o.id === this.form.host)
      const r = await this.portScan(host.addresses[0])
      this.scan.results = Object.keys(r.ports).filter(k => r.ports[k] === 'open')
    },

    portScan(host, port=null) {
      this.scan.scanning = true
      return new Promise((resolve) => {
        const data = {
          host,
        }
        if (port) {
          data['ports'] = [port]
        }
        axios
          .post('/api/hosts/port_scan/', data, { params: {'only_open': 'true' }})
          .then((r) => {
            this.scan.scanning = false;
            resolve(r.data)
          })
          .catch(() => {
            this.scan.scanning = false;
            resolve(false)
          })
      })
    }
  }
}
</script>

<style scoped>

</style>
