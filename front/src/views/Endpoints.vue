<template>
  <div>
    <button
      @click="adding=!adding"
    >+</button>
    <endpoint
      v-if="adding"
      :editing="true"
    ></endpoint>
  </div>
</template>

<script>
import Endpoint from '../components/Endpoint.vue'

export default {
  name: 'Endpoints',

  components: {
    Endpoint
  },

  data () {
    return {
      adding: false
    }
  }
}
</script>

<style scoped>

</style>
