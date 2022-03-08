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
            :value="active.length"
            :content="active.length"
          >
            <v-icon
              :class="{ rotating: active.length }"
            >mdi-cog-outline</v-icon>
          </v-badge>
        </v-btn>
      </template>
      <v-list
        v-if="tasks.length > 0"
      >
        <v-list-item
          v-for="(item, index) in tasks"
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
    })
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
</style>
