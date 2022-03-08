<template>
  <div>
    <v-form>
      <v-row>
        <v-col>
          <v-select
            v-model="form.type"
            :items="domainTypes"
            item-value="id"
            item-text="name"
            label="Domain type"
          ></v-select>
        </v-col>
      </v-row>
      <div
        v-if="form.type === 'shared'"
      >
        <v-row>
          <v-col>
            <SharedDomain/>
          </v-col>
        </v-row>
      </div>
      <div
        v-else
      >
        <v-row>
          <v-col>
            <v-text-field
              label="Hostname"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row v-if="form.type !== 'manual'">
          <v-col>
            <v-text-field
              v-for="(option, i) in options"
              :key="i"
              :label="option"
            ></v-text-field>
          </v-col>
        </v-row>
      </div>
    </v-form>
  </div>
</template>

<script>
import axios from 'axios'
import SharedDomain from '@/components/SharedDomain'

export default {
  name: 'HostAddress',

  components: {
    SharedDomain
  },

  data () {
    return {
      form: {
        type: null,
      },
      providers: null,
      options: null,
      shared: null,
    }
  },

  mounted () {
    axios
      .get('/api/domains/providers/')
      .then((r) => {
        this.providers = r.data
      })
      .catch(console.error)
  },

  computed: {
    domainTypes () {
      const types = [
        { id: 'shared', name: 'Shared domain - https://homeland.social'},
        { id: 'manual', name: 'Manual domain'},
      ]

      if (this.providers) {
        Object.keys(this.providers).forEach(name => {
          const provider = this.providers[name]
          types.push({ id: name, name: `${name} - ${provider.url}` })
        })
      }

      return types
    },
  },

  watch: {
    'form.type' (val) {
      if (val !== 'manual') {
        const params = {
          type: 'dynamic',
          provider: val,
        }
        axios
          .get('/api/domains/options/', { params })
          .then((r) => {
            this.options = r.data
          })
          .catch(console.error)
      }
    }
  },
}
</script>

<style scoped>

</style>
