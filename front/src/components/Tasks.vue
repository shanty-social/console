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
            :value="tasks.length"
            :content="tasks.length"
          >
            <v-icon
              :class="{ rotating: active.length }"
            >mdi-cog-outline</v-icon>
          </v-badge>
        </v-btn>
      </template>

      <v-card
        v-if="tasks.length > 0"
      >
        <v-list
          class="scroll-list"
        >
          <v-list-item
            v-for="(item, index) in tasks"
            :key="index"
          >
            <v-list-item-icon>
              <v-icon>{{ taskIcon(item) }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ item.function }}</v-list-item-title>
            <v-list-item-icon>
              <v-icon
                class="text-right"
                @click.stop.prevent="deleteTask(item.id)"
              >mdi-delete</v-icon>
            </v-list-item-icon>
          </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list>
          <v-list-item>
            <v-list-item-content>
              <v-btn
                @click="clearTasks"
              >
                Clear all
              </v-btn>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Tasks',

  data () {
    return {
      user: null
    }
  },

  computed: {
    ...mapGetters({ tasks: 'tasks/data' }),

    active () {
      return this.tasks.filter(o => o.completed === null)
    }
  },

  methods: {
    ...mapActions({
      fetchTasks: 'tasks/fetch',
      deleteTask: 'tasks/delete',
      clearTasks: 'tasks/clear',
    }),

    taskIcon (task) {
      if (!task.completed) {
        return 'mdi-cog-outline'
      } else if (task.result && task.result.type === 'Exception') {
        return 'mdi-alert-circle-outline'
      } else {
        return 'mdi-check-outline'
      }
    },
  },

  mounted () {
    this.fetchTasks()
  }
}
</script>

<style scoped>
@keyframes rotating {
  from {
    transform: rotate(0deg);
    -o-transform: rotate(0deg);
    -ms-transform: rotate(0deg);
    -moz-transform: rotate(0deg);
    -webkit-transform: rotate(0deg);
  }
  to {
    transform: rotate(60deg);
    -o-transform: rotate(60deg);
    -ms-transform: rotate(60deg);
    -moz-transform: rotate(60deg);
    -webkit-transform: rotate(60deg);
  }
}

@-webkit-keyframes rotating {
  from {
    transform: rotate(0deg);
    -webkit-transform: rotate(0deg);
  }
  to {
    transform: rotate(60deg);
    -webkit-transform: rotate(60deg);
  }
}

.rotating {
  -webkit-animation: rotating 0.5s linear infinite;
  -moz-animation: rotating 0.5s linear infinite;
  -ms-animation: rotating 0.5s linear infinite;
  -o-animation: rotating 0.5s linear infinite;
  -o-animation: rotating 0.5s linear infinite;
  animation: rotating 0.5s linear infinite;
}

.scroll-list {
  max-height: 300px;
  overflow-y: auto;
}
</style>
