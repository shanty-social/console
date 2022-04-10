<template>
  <v-form
    @submit.prevent="onCreate"
    ref="form"
  >
    <p class="text-h4">Host / server</p>
    <p>First choose a container and port to expose. Choose a container, and then a port once the list is populated.</p>
    <v-row>
      <v-col md="8">
        <v-select
          v-model="form.host.name"
          :items="hosts"
          item-value="name"
          :item-text="item => `${item.hostname} - ${item.image}`"
          :rules="rules.host"
          placeholder="choose a container"
          @change="() => { scan(); update(); }"
          label="Choose container"
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
          :hide-spin-buttons="true"
          @change="update"
          label="Select or enter port"
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
        host: (this.value) ? this.value.host : {},
        port: (this.value) ? this.value.port : null,
      },
      rules: {
        host: [
          v => (v !== undefined) || 'Is required'
        ],
        port: [
          v => (v > 0) || 'Choose a port'
        ],
      },
      error: null,
      busy: false,
      ports: null,
    }
  },

  mounted () {
    this
      .fetch()
      .then(() => {
        this.populateValue()
      })
  },

  computed: {
    ...mapGetters({ hosts: 'hosts/data' }),

    host () {
      return this.hosts.find((o) => o.name === this.form.host.name)
    },
  },

  watchers: {
    value () {
      this.populateValue()
    }
  },

  methods: {
    ...mapActions({ fetch: 'hosts/fetch' }),

    populateValue () {
      if (!this.value) {
        return
      }

      if (this.value.port) {
        this.form.port = this.value.port
      } else {
        this.scan()
      }

      if (this.value.host && this.value.host.name && !this.value.host.addr) {
        const host = this.hosts.find((o) => o.name === this.value.host.name)
        if (host) {
          this.value.host.addr = host.aliases[0]
        }
      } else if (this.value.host && this.value.host.addr && !this.value.host.name) {
        const host = this.hosts.find((o) => o.aliases.includes(this.value.host.addr))
        if (host) {
          this.value.host.name = host.name
        }
      }
    },

    update () {
      this.$emit('input', {
        host: {
          name: this.form.host.name,
          addr: this.host.aliases[0],
        },
        port: this.form.port,
      })
    },

    scan() {
      if (!this.host) {
        return
      }
      this.busy = true
      this.ports = null
      const data = {
        host: this.host.addresses[0]
      }
      axios
        .post('/api/hosts/port_scan/', data, { params: {'only_open': 'true' }})
        .then((r) => {
          this.busy = false;
          this.ports = []
          this.host.ports.forEach((port) => {
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
