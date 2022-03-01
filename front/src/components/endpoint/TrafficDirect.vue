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
        v-text="item"
      />
    </ul>
    <v-row class="mt-4">
      <v-col>
        <v-text-field
          v-model="form.httpPort"
          :rules="rules.httpPort"
          label="HTTP port"
          type="number"
        >HTTP Port</v-text-field>
      </v-col>
      <v-col>
        <v-text-field
          v-model="form.httpsPort"
          :rules="rules.httpsPort"
          label="HTTPS port"
          type="number"
        >HTTPS Port</v-text-field>
      </v-col>
      <v-col>
        <v-btn>Configure automatically</v-btn>
      </v-col>
    </v-row>
  </p>
</template>

<script>
export default {
  name: 'TrafficDirect',

  data () {
    return {
      form: {
        httpPort: 80,
        httpsPort: 443
      },
      rules: {
        httpPort: [],
        httpsPort: [],
      },
      ratings: [
        { label: 'Privacy', level: 'low', color: 'red', icon: 'mdi-gauge-empty' },
        { label: 'Skill', level: 'medium', color: 'yellow', icon: 'mdi-gauge', },
        { label: 'Effciency', level: 'high', color: 'green', icon: 'mdi-gauge-full', },
        { label: 'Censorproof', level: 'medium', color: 'yellow', icon: 'mdi-gauge', },
      ],
      info: [
        'This method exposes your IP address',
        'Your IP address reveals your general location and possibly your identity',
        'Ports must be opened in your router, it may be possible for this to be done automatically',
        'This method has no external dependencies and traffic flows over the shortest path',
      ]
    }
  }
}
</script>

<style scoped>

</style>