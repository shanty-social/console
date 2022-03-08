<template>
  <v-form
    @submit.prevent="onCreate"
    ref="form"
  >
    <p class="text-h4">Traffic delivery</p>
    <p>You need to configure a method for traffic delivery.</p>
    <v-radio-group
      v-model="form.method"
      @change="update"
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
      :is="selectedMethod.component"
      v-if="selectedMethod"
      v-model="form.options"
    />
    <v-alert
      v-if="error"
      dense outlined
      type="error"
    >{{ error }}</v-alert>
  </v-form>
</template>

<script>
import TrafficDirect from '@/components/endpoint/TrafficDirect'
import TrafficTunnel from '@/components/endpoint/TrafficTunnel'
import TrafficTor from '@/components/endpoint/TrafficTor'

export default {
  name: 'Traffic',

  components: {
    TrafficDirect,
    TrafficTunnel,
    TrafficTor,
  },

  props: {
    value: {
      type: Object,
      default: null,
    }
  },

  data () {
    return {
      form: {
        method: (this.value) ? this.value.method : null,
        options: null,
      },
      methods: {
        Direct: { description: 'traffic is sent directly to your home router', component: TrafficDirect },
        Tunnel: { description: 'traffic is sent to homeland social servers then routed over an encrypted tunnel', component: TrafficTunnel },
        TOR: { description: 'traffic arrives via the TOR network. This method requires users to use a special browser', component: TrafficTor },
      },
      error: null,
    }
  },

  computed: {
    selectedMethod () {
      return this.methods[this.form.method]
    }
  },

  watch: {
    'form.options' () {
      this.update()
    }
  },

  methods: {
    update () {
      this.$emit('input', {
        method: this.form.method,
        options: this.form.options,
      })
    }
  }
}
</script>

<style scoped>

</style>
