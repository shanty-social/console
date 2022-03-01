<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout justify-center>
        <v-flex xs12 sm8 md6>
          <v-card class="elevation-12">
            <v-toolbar dark color="primary">
              <v-toolbar-title>Create Endpoint</v-toolbar-title>
            </v-toolbar>
            <v-card-text>
              <v-expansion-panels
                :value="step"
              >
                <v-expansion-panel
                  v-for="(step, i) of steps"
                  :key="i"
                >
                  <v-expansion-panel-header
                    disable-icon-rotate
                  >
                    {{ step.name }}
                    <template v-slot:actions>
                      <v-icon
                        :color="(steps[i].valid) ? 'green' : ''"
                      >mdi-check-bold</v-icon>
                    </template>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <component :is="steps[i].component"
                      @status="(valid) => onStatus(i, valid)"
                    />
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>
import EndpointHost from '@/components/endpoint/Host'
import EndpointTraffic from '@/components/endpoint/Traffic'
import EndpointAddress from '@/components/endpoint/Address'

export default {
  name: 'Endpoint',

  components: {
    EndpointHost,
    EndpointTraffic,
    EndpointAddress,
  },

  data () {
    let host = this.$route.query.host
    if (host) {
      host = decodeURI(host)
    }

    return {
      host,
      steps: [
        { name: 'Host', component: EndpointHost, valid: false },
        { name: 'Traffic', component: EndpointTraffic, valid: false },
        { name: 'Address', component: EndpointAddress, valid: false }
      ],
      step: 0
    }
  },

  methods: {
    onStatus (step, valid) {
      this.steps[step].valid = valid
      if (!valid) return
      if (step++ > this.steps.length) {
        return
      }
      this.step = step
    }
  }
}
</script>

<style scoped>

</style>
