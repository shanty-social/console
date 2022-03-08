<template>
  <div>
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
    <TorAddress
      v-model="form.address"
      @change="update"
    />
  </div>
</template>

<script>
import TorAddress from '@/components/TorAddress'

export default {
  name: 'TrafficTor',

  components: {
    TorAddress,
  },

  props: {
    value: Object,
  },

  data () {
    return {
      form: {
        address: null,
      },
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
        'All traffic is encrypted end-to-end',
      ],
    }
  },

  methods: {
    update () {
      this.$emit('input', { address: this.form.address })
    }
  }
}
</script>

<style scoped>

</style>