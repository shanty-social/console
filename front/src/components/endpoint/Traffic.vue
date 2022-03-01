<template>
  <v-form
    @submit.prevent="onCreate"
    ref="form"
  >
    <p>You need to configure a method for traffic delivery.</p>
    <v-radio-group
      v-model="form.method"
    >
      <v-radio
        v-for="(name, i) of Object.keys(methods)"
        :key="i"
        :label="name"
        :value="name"
      >
        <template v-slot:label>
          <strong>{{ name }}</strong>&nbsp;
          {{ methods[name].description }}
        </template>
      </v-radio>
    </v-radio-group>
    <component
      v-if="selectedMethod"
      :is="selectedMethod.component"
    />
    <v-alert
      v-if="error"
      dense outlined
      type="error"
    >{{ error }}</v-alert>
    <v-btn type="submit">
      Next
      <v-icon>mdi-menu-right</v-icon>
    </v-btn>
  </v-form>
</template>

<script>
import TrafficDirect from '@/components/endpoint/TrafficDirect'
import TrafficTunnel from '@/components/endpoint/TrafficTunnel'
import TrafficTOR from '@/components/endpoint/TrafficTOR'

export default {
  name: 'Traffic',

  components: {
    TrafficDirect,
    TrafficTunnel,
    TrafficTOR
  },

  data () {
    return {
      form: {
        method: 'Direct'
      },
      methods: {
        Direct: { description: 'traffic is sent directly to your home router', component: TrafficDirect },
        Tunnel: { description: 'traffic is sent to homeland social servers then routed over an encrypted tunnel', component: TrafficTunnel },
        TOR: { description: 'traffic arrives via the TOR network. This method requires users to use a special browser', component: TrafficTOR },
      },
      error: null,
    }
  },

  computed: {
    selectedMethod () {
      return this.methods[this.form.method]
    }
  },

  mounted () {
  },

}
</script>

<style scoped>

</style>
