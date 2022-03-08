<template>
  <div class="mr-2">
    <v-menu>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          dark
          v-bind="attrs"
          v-on="on"
        >
          <v-badge
            color="deep-purple"
            :value="messages.length"
            :content="messages.length"
          >
            <v-icon
              :class="{ rotating: messages.length }"
            >mdi-email-outline</v-icon>
          </v-badge>
        </v-btn>
      </template>
      <v-list
        v-if="messages.length > 0"
      >
        <v-list-item
          v-for="(item, index) in messages"
          :key="index"
        >
          {{ item.function }}
          <v-list-item-action>
            <v-icon
              right
              @click="deleteTask(item.id)"
            >mdi-delete</v-icon>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Messages',

  data () {
    return {}
  },

  mounted () {
    this.fetchMessages()
  },

  computed: {
    ...mapGetters({ messages: 'messages/data' }),
  },

  methods: {
    ...mapActions({ fetchMessages: 'messages/fetch' }),
  }
}
</script>

<style scoped>

</style>
