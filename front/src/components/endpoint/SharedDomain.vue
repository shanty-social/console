<template>
  <v-form>
    <p class="text-h4">Domain</p>
    <p>Next choose a domain name. Use the arrows to select a suffix, then type a prefix.</p>
    <v-text-field
      v-model="form.hostname"
      :prefix="suffix"
      :rules="rules.hostname"
      :error-messages="errors"
      prepend-inner-icon="mdi-menu-right"
      append-icon="mdi-menu-left"
      placeholder="enter a prefix"
      @click:prepend-inner="decrement"
      @click:append="increment"
      @change="update"
      reverse
    ></v-text-field>
  </v-form>
</template>

<script>
import api from '@/services/api'
import debounce  from 'debounce'

export default {
  name: 'SharedDomain',

  props: {
    value: String,
  },

  data () {
    let hostname = null
    if (this.value) {
      hostname = this.value.split('.')[0]
    }

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
      editing: this.value,
      shared: null,
      index: 0,
      errors: [],
    }
  },

  computed: {
    suffix () {
      return (this.shared) ? `.${this.shared[this.index]}` : null
    }
  },

  watch: {
    'form.hostname' (val) {
      this.check(val)
    },

    value (val) {
      this.form.hostname = val.split('.')[0]
      this.editing = val
    }
  },

  mounted () {
    api
      .get('/api/oauth/shanty/domains/')
      .then((r) => {
        this.shared = r.data
        if (this.value) {
          const domain = this.value.split('.').slice(1).join('.')
          this.index = this.shared.indexOf(domain)
        }
      })
      .catch(console.error)
  },

  methods: {
    decrement () {
      this.index -= 1
      if (this.index < 0) {
        this.index = this.shared.length - 1;
      }
      this.update()
    },

    increment () {
      this.index += 1
      if (this.index === this.shared.length) {
        this.index = 0
      }
      this.update()
    },

    update () {
      this.$emit('input', `${this.form.hostname}${this.suffix}`)
    },

    check: debounce(function(val) {
      const domain = `${val}${this.suffix}`
      if (domain === this.editing) {
        this.errors = []
        return
      }
      api
        .post(`/api/oauth/shanty/check_domain/`, { name: domain })
        .then(() => {
          this.errors = ['Is not available']
        })
        .catch((e) => {
          if (e.response.status === 404) {
            this.errors = []
          }
        })
    }, 1000),
  },
}
</script>

<style scoped>

</style>
