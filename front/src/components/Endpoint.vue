<template>
  <div>
    <form
      v-if="editing"
      @submit.prevent="onSave"
    >
      <input v-model="form.name" type="text" name="name" placeholder="name" size="10"/>
      <select v-model="form.host" name="host">
        <option
          v-for="(host, index) in hosts"
          v-bind:key="index"
          v-bind:value="host.service"
        >{{ host.service }}</option>
      </select>
      <input v-model="form.http_port" type="integer" name="name" size="3"/>
      <input v-model="form.https_port" type="integer" name="name" size="3"/>
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
        http_port: 80,
        https_port: 443,
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
    }
  }
}
</script>

<style scoped>

</style>
