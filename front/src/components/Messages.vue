<template>
  <div class="mr-2">
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn
          dark
          v-bind="props"
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
      <v-card
        v-if="messages.length > 0"
      >
        <v-list
          class="scroll-list"
        >
          <v-list-item
            v-for="(item, index) in messages"
            :key="index"
          >
            <v-list-item-title>{{ item.subject }}</v-list-item-title>
            <template v-slot:prepend>
              <v-icon
                class="text-right"
                @click.stop.prevent="deleteMessage(item.id)"
              >mdi-delete</v-icon>
            </template>
          </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list>
          <v-list-item>
            <v-btn
              @click="clearMessages"
            >
              Clear all
            </v-btn>
          </v-list-item>
        </v-list>
      </v-card>
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
    ...mapActions({
      fetchMessages: 'messages/fetch',
      deleteMessage: 'messages/delete',
      clearMessages: 'messages/clear',
    }),
  }
}
</script>

<style scoped>
.scroll-list {
  max-height: 300px;
  overflow-y: auto;
}
</style>
