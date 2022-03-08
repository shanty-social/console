<template>
  <v-combobox
    v-model="form.selected"
    :rules="rules.prefix"
    :hint="prefixHint"
    :items="torAddresses"
    item-text="hostname"
    item-value="id"
    label="Address prefix"
    class="mt-2"
    :append-outer-icon="busy ? 'mdi-close-octagon' : 'mdi-play'"
    :loading="busy"
    @click:append-outer="toggleGenerate"
    @update:search-input="val => form.prefix = val"
  >
    <template v-slot:progress>
      <v-progress-linear
        absolute
        indeterminate
        height="2"
      ></v-progress-linear>
    </template>
  </v-combobox>
</template>

<script>
import axios from 'axios'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'TorAddress',

  props: {
    value: Object,
  },

  data () {
    return {
      form: {
        prefix: null,
        selected: this.value,
      },
      rules: {
        prefix: [
          v => (v || '').length <= 10 || 'Too long',
          v => (v || '').match(/^[A-Za-z0-9/]*$/) !== null || 'Invalid characters'
        ],
      },
      hints: [
        'Less than a second',
        'Less than a second',
        'Less than a second',
        'A couple seconds',
        'About a minute',
        'About half an hour',
        'About a day',
        'Almost a month',
        'More than two years',
        'More than your lifetime'
      ],
      id: null,
    }
  },

  mounted () {
    this.fetchTorAddresses()
  },

  watch: {
    current () {
      if (!this.current || !this.current.completed) return
      this.fetchTorAddresses()
      this.id = null
      this.form.prefix = null
    }
  },

  computed: {
    ...mapGetters({
      tasks: 'tasks/data',
      torAddresses: 'tor/data',
    }),

    prefixHint () {
      const no = Math.min((this.form.prefix || '').length, this.hints.length - 1)
      return this.hints[no]
    },

    current () {
      return this.tasks.find(o => o.id === this.id) || null
    },

    busy () {
      return this.id !== null
    },
  },

  methods: {
    ...mapActions({
      fetchTorAddresses: 'tor/fetch',
      deleteTorAddress: 'tor/delete',
      deleteTask: 'tasks/delete',
    }),

    toggleGenerate () {
      if (this.id === null) {
        axios
          .post('/api/tor/generate/', { prefix: this.form.prefix })
          .then((r) => {
            this.id = r.data.id
          })
          .catch(console.error)
      } else {
        this.deleteTask(this.id)
      }
    },

    update () {
      this.$emit('input', this.torAddresses[this.form.selected])
      this.$emit('change')
    }
  },
}
</script>

<style scoped>

</style>
