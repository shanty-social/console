<template>
  <p
    class="mt-4"
  >
    <v-chip
      v-for="(rating, i ) of ratings"
      :key="i"
      :color="rating.color"
      class="ml-2"
      pill
    >
      {{ `${rating.label}: ${rating.level}` }}
      <v-icon
        v-text="rating.icon"
        class="ml-1"
      ></v-icon>
    </v-chip>
    <ul class="mt-4">
      <li
        v-for="(item, i) of info"
        :key="i"
        v-html="item"
      />
    </ul>
    <v-row class="mt-4">
      <v-col>
        <v-text-field
          v-model="form.prefix"
          :rules="rules.prefix"
          :hint="prefixHint"
          counter="8"
          :counter-value="v => (v || '').trim().length"
          label="Address prefix"
          type="string"
        >Address prefix</v-text-field>
      </v-col>
      <v-col>
        <v-btn
          @click.prevent="generateAddress"
        >Generate address</v-btn>
      </v-col>
    </v-row>
    <v-progress-linear
      v-model="progress"
      :active="progress !== 0"
      class="mt-4"
    ></v-progress-linear>
  </p>
</template>

<script>
import axios from 'axios'

export default {
  name: 'TrafficTOR',

  data () {
    return {
      form: {
        prefix: null,
      },
      rules: {
        prefix: [
          v => (v || '').length <= 10 || 'Too long',
          v => (v || '').match(/^[A-Za-z0-9+/]*$/) !== null || 'Invalid characters'
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
      ratings: [
        { label: 'Privacy', level: 'high', color: 'green', icon: 'mdi-gauge-full' },
        { label: 'Skill', level: 'high', color: 'red', icon: 'mdi-gauge-empty', },
        { label: 'Effciency', level: 'low', color: 'red', icon: 'mdi-gauge-empty', },
        { label: 'Censorproof', level: 'high', color: 'green', icon: 'mdi-gauge-full', },
      ],
      info: [
        'This method provides anonymity when configured properly',
        'Users must use a specialized browser (the <a target="_new" href="https://www.torproject.org/download/">tor browser</a>) to view your site',
        'Traffic is routed over a peer-to-peer network to hide your identity',
      ],
      address: {
        poller: null,
        stats: null,
        result: null,
      },
    }
  },

  computed: {
    prefixHint () {
      const no = Math.min((this.form.prefix || '').length, this.hints.length - 1)
      return this.hints[no]
    },

    progress () {
      const stats = this.address.stats
      if (stats && stats.elapsed && stats.estimate) {
        return stats.elapsed / stats.estimate * 100
      }
      return 0
    }
  },

  methods: {
    generateAddress () {
      axios
        .post('/api/tor/generate/', this.form)
        .then(() => {
          // this.address.poller = setInterval(this.pollTask.bind(this), 1000, r.data.id)
        })
        .catch(console.error)
    },

    pollTask(id) {
      axios
        .get(`/api/tasks/${id}/`)
        .then((r) => {
          this.address.stats = r.data.tail
          if (r.data.completed) {
            clearInterval(this.address.poller)
            this.address.result = r.data.result[0]
            this.address.poller = null
          }
        })
        .catch(console.error)
    }
  }
}
</script>

<style scoped>

</style>