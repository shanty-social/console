<template>
  <v-form
    @submit.prevent="onCreate"
    ref="form"
  >
    <p class="text-h4">Host / server</p>
    <p>First we need a service and port to expose. Choose a host and an open port.</p>
    <v-row>
      <v-col md="8">
        <v-select
          v-model="form.host"
          :items="hosts"
          :item-text="item => `${item.hostname} - ${item.image}`"
          return-object
          :rules="rules.host"
          placeholder="choose host"
          @change="scan"
          label="Select host"
          :loading="busy"
        >
          <template v-slot:progress>
            <v-progress-linear
              height="2"
              indeterminate
              absolute
            ></v-progress-linear>
          </template>
        </v-select>
      </v-col>
      <v-col md="4">
        <v-combobox
          v-model="form.port"
          :rules="rules.port"
          :items="ports"
          :disabled="ports === null"
          :hide-spin-buttons="true"
          @change="update"
          label="Select port"
          type="number"
        ></v-combobox>
      </v-col>
    </v-row>
    <v-alert
      v-if="error"
      dense outlined
      type="error"
    >{{ error }}</v-alert>
  </v-form>
</template>

<script>
import axios from 'axios'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Host',

  props: {
    value: {
      type: Object,
      default: null
    }
  },

  data () {
    return {
      form: {
        host: (this.value) ? this.value.host : null,
        port: (this.value) ? this.value.port : null,
        other: null
      },
      rules: {
        host: [
          v => (v !== undefined) || 'Is required'
        ],
        port: [
          v => (v > 0 || v === 'other') || 'Choose a port'
        ],
      },
      error: null,
      busy: false,
      ports: null,
    }
  },

  mounted () {
    this.fetchHosts()
  },

  computed: {
    ...mapGetters({ hosts: 'hosts/data' }),
  },

  methods: {
    ...mapActions({ fetchHosts: 'hosts/fetch' }),

    update () {
      this.$emit('input', {
        host: this.form.host,
        port: this.form.port,
      })
    },

    scan() {
      this.busy = true
      this.ports = null
      const data = {
        host: this.form.host.addresses[0]
      }
      axios
        .post('/api/hosts/port_scan/', data, { params: {'only_open': 'true' }})
        .then((r) => {
          this.busy = false;
          this.ports = []
          this.form.host.ports.forEach((port) => {
            this.ports.push(port)
          })
          Object.keys(r.data.ports).forEach(port => {
            port = parseInt(port, 10)
            if (!this.ports.includes(port)) {
              this.ports.push(port)
            }
          })
          if (this.ports.length === 1) {
            this.form.port = this.ports[0]
            this.update()
          }
        })
        .catch(() => {
          this.busy = false;
        })
    }
  },
}
</script>

<style scoped>

</style>
