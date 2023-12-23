<template>
  <v-app>
    <v-toolbar density="compact" title="SlipOS">
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon color="green">mdi-ethernet</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>mdi-wifi</v-icon>
      </v-btn>
    </v-toolbar>

    <div
      id="screen"
    >

      <Window
        v-for="(window, i) in windows"
        :title="window.title"
        :src="window.src"
        :initialX="i * 40"
        :initialY="i * 40"
        :focused="window.order === windows.length"
        :style="{ zIndex: window.order }"
        @focus="focus(i)"
        @close="close(i)"
      ></Window>
    </div>
  </v-app>
</template>

<script>
import options from '../services/options.js';
import Window from '../components/desktop/Window.vue.js';

export default {
  name: "Desktop",

  components: {
    Window,
  },

  data() {
    const windows = [];

    for (let i = 1; i < 10; i++) {
      windows.push({
        title: `Test Window #${i}`,
        src: null,
        order: i,
      })
    }

    return {
      windows,
    };
  },

  beforeCreate() {
    document.body.style.backgroundImage = `url(${options.wallpaper})`;
  },

  methods: {
    focus(index) {
      const currOrder = this.windows[index].order;
      const topOrder = this.windows.length;
      this.windows.forEach((window, i) => {
        if (window.order > currOrder) {
          window.order--;
        }
      });
      this.windows[index].order = topOrder;
    },

    close(index) {
      this.windows.splice(index, 1);
    },
  },
}
</script>

<style>
#screen {
  position: relative;
  width: 100%;
  height: 100%;
}
</style>
