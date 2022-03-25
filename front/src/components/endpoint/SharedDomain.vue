<template>
  <v-form>
    <p class="text-h4">Domain</p>
    <p>Next we need to choose a domain name. This is what users will type into their browser to visit your site.</p>
    <v-text-field
      v-model="form.hostname"
      :prefix="suffix"
      :rules="rules.hostname"
      :error-messages="errors"
      prepend-inner-icon="mdi-menu-right"
      append-icon="mdi-menu-left"
      @click:prepend-inner="decrement"
      @click:append="increment"
      @change="update"
      reverse
    ></v-text-field>
  </v-form>
</template>

<script>
import axios from 'axios'
import { debounce}  from 'debounce'

export default {
  name: 'SharedDomain',

  props: {
    value: String,
  },

  data () {
    const hostname = this.value || null
    return {
      form: {
        hostname,
      },
      rules: {
        hostname: [
          v => (v || '').length > 0 || 'Is required',
          v => (v || '').length < 32 || 'Is too long',
          v => (v || '').match(/^[A-Za-z0-9-/]*$/) !== null || 'Invalid characters',
        ]
      },
      shared: null,
      current: 0,
      errors: [],
    }
  },

  computed: {
    suffix () {
      return (this.shared) ? `.${this.shared[this.current]}` : null
    }
  },

  watch: {
    'form.hostname' (val) {
      this.check(val)
    },
  },

  mounted () {
    axios
      .get('/api/domains/shared/')
      .then((r) => {
        this.shared = r.data
      })
      .catch(console.error)
  },

  methods: {
    decrement () {
      this.current -= 1
      if (this.current < 0) {
        this.current = this.shared.length - 1;
      }
    },

    increment () {
      this.current += 1
      if (this.current === this.shared.length) {
        this.current = 0
      }
    },

    update () {
      this.$emit('input', `${this.form.hostname}${this.suffix}`)
    },

    check: debounce(function(val) {
      axios
        .post(`/api/domains/check/`, { name: `${val}${this.suffix}` })
        .then(() => {
          this.errors = ['Is not available']
        })
        .catch((e) => {
          if (e.response.statusCode === 404) {
            this.errors = []
          }
        })
    }, 1000),
  },
}
</script>

<style scoped>

</style>
