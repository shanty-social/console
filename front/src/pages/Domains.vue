<template>
  <div>
    <button
      @click="adding=!adding"
    >+</button>
    <domain
      v-if="adding"
      :editing="true"
    ></domain>
  </div>
</template>

<script>
import Domain from '../components/Domain.vue'

export default {
  name: 'Domains',

  components: {
    Domain
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
