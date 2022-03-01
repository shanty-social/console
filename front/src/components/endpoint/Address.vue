<template>
  <v-form
    @submit.prevent="onCreate"
    ref="form"
  >
    <p>Finally, you will need an address for users to use when acessing your site.</p>
  </v-form>
</template>

<script>
export default {
  name: 'Address',

  data () {
    return {
    }
  },

  mounted () {
  },

}
</script>

<style scoped>

</style>
