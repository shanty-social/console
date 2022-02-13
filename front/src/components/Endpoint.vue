<template>
  <div>
    <form
      v-if="editing"
      @submit.prevent="onSave"
    >
      <input v-model="form.name" type="text" name="name" placeholder="name" size="10"/>
      <select
        @change="onHostChange"
        v-model="form.host"
        name="host"
      >
        <option
          v-for="(host, index) in hosts"
          v-bind:key="index"
          v-bind:value="host.service"
        >{{ host.service }}</option>
      </select>
      <input
        v-if="form.type=='direct'"
        v-model="form.http_port_external"
        type="integer"
        name="http_external"
        size="3"
      />
      <span
        v-if="form.type=='direct'"
      >-&gt;</span>
      <input v-model="form.http_port_internal" size="3"/>
      <input
        v-if="form.type=='direct'"
        v-model="form.https_port_external"
        type="integer"
        name="https_external"
        size="3"
      />
      <span
        v-if="form.type=='direct'"
      >-&gt;</span>
      <input
        v-if="form.type=='direct'"
        v-model="form.https_port_internal"
        size="3"
      />
      <input v-model="form.path" type="text" name="name" size="12"/>
      <select v-model="form.type" name="name">
        <option value="direct" default>direct</option>
        <option value="tunnel">tunnel</option>
      </select>
      <select v-model="form.domain" name="domain">
        <option
          v-for="(domain, index) in domains"
          v-bind:key="index"
          v-bind:value="domain.name"
        >{{ domain.name }}</option>
      </select>
      <button type="submit">Save</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Endpoint',

  props: {
    editing: {
      type: Boolean,
      default: false
    }
  },

  data () {
    return {
      form: {
        name: null,
        host: null,
        http_port_external: 80,
        http_port_internal: null,
        https_port_external: 443,
        https_port_internal: null,
        path: '/',
        type: 'direct',
        domain: null
      },
      domains: [],
      hosts: []
    }
  },

  mounted () {
    axios
      .get('/api/hosts/')
      .then((r) => {
        this.hosts = r.data.objects
      })
      .catch(console.error)
    axios
      .get('/api/domains/')
      .then((r) => {
        this.domains = r.data.objects
      })
      .catch(console.error)
  },

  methods: {
    onSave () {
      axios
        .post('/api/endpoints/', this.form)
        .then((r) => {
          console.log(r.data)
        })
        .catch(console.error)
    },

    onHostChange () {
      const host = this.hosts.find(o => o.service === this.form.host)
      const tcpPorts = host.ports.filter(o => o.indexOf('tcp') !== -1)

      // Select defaults:
      const httpPort = tcpPorts.find(o => o.indexOf('80') !== -1)
      if (httpPort) {
        this.form.http_port_internal = parseInt(httpPort.split('/')[0], 10)
      }
      const httpsPort = tcpPorts.find(o => o.indexOf('443') !== -1)
      if (httpsPort) {
        this.form.https_port_internal = parseInt(httpsPort.split('/')[0], 10)
      }
    }
  }
}
</script>

<style scoped>

</style>
