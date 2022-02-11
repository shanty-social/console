<template>
  <div>
    <form
      v-if="editing"
      @submit.prevent="onSave"
    >
      <input v-model="form.name" type="text" placeholder="name" size="12"/>
      <select
        v-model="form.type"
        name="type"
        @change="getOptions"
      >
        <option
          v-for="(type, index) in types"
          v-bind:key="index"
          v-bind:value="type"
        >{{ type }}</option>
      </select>
      <select
        v-model="form.provider"
        name="provider"
        @change="getOptions"
      >
        <option
          v-for="(provider, index) in providers"
          v-bind:key="index"
          v-bind:value="provider"
        >{{ provider }}</option>
      </select>
      <input
        v-for="(option, index) in Object.keys(options)"
        v-bind:key="index"
        v-bind:name="option"
        v-model="options[option]"
        v-bind:placeholder="option"
        size="12"
      />
      <button type="submit">Save</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Domain',

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
        type: 'dynamic',
        provider: null
      },
      options: [],
      types: ['static', 'dynamic'],
      providers: []
    }
  },

  mounted () {
    axios
      .get('/api/domains/providers/')
      .then((r) => {
        this.providers = Object.keys(r.data)
      })
      .catch(console.error)
  },

  methods: {
    getOptions () {
      const { type, provider } = this.form

      if (!type || !provider) {
        return
      }

      axios
        .get('/api/domains/options/', {params: {type, provider}})
        .then((r) => {
          // Update options and preserve values.
          const options = {}
          for (const name of r.data) {
            options[name] = this.options[name]
          }
          this.options = options
        })
        .catch(console.error)
    },

    onSave () {
      const data = {...this.form, options: this.options}
      axios
        .post('/api/domains/', data)
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
