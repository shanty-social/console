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
        v-text="item"
      />
    </ul>
    <HostAddress/>
  </div>
</template>

<script>
import HostAddress from '@/components/HostAddress'

export default {
  name: 'TrafficTunnel',

  components: {
    HostAddress,
  },

  data () {
    return {
      ratings: [
        { label: 'Privacy', level: 'medium', color: 'yellow', icon: 'mdi-gauge' },
        { label: 'Skill', level: 'low', color: 'green', icon: 'mdi-gauge-full', },
        { label: 'Effciency', level: 'medium', color: 'yellow', icon: 'mdi-gauge', },
        { label: 'Censorproof', level: 'low', color: 'red', icon: 'mdi-gauge-empty', },
      ],
      info: [
        'This method hides your IP address',
        'Traffic is routed over an encrypted tunnel to your server',
        'No ports are opened in your router',
        'A 3rd party proxy server is required',
      ]
    }
  }
}
</script>

<style scoped>

</style>