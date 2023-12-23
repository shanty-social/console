<template>
  <div
    id="window"
    :style="{ width: `${width}px`, height: `${height}px`, borderColor: options.theme.borderColor, top: `${y}px`, left: `${x}px` }"
    @mousedown.prevent="$emit('focus')"
  >
    <div
      class="toolbar"
      :style="{ backgroundColor: options.theme.borderColor, width: `${width}px`, cursor: (action.dragging) ? 'move' : 'grab' }"
      @mousedown.prevent="startDrag"
    >
      <p id="title">{{ title }}</p>
      <v-icon
        size="16"
        color="white"
        class="toolbar-icon"
        @click="$emit('close')"
      >mdi-close-box-outline</v-icon>
      <v-icon
        size="16"
        color="white"
        class="toolbar-icon"
      >mdi-window-maximize</v-icon>
      <v-icon
        size="16"
        color="white"
        class="toolbar-icon"
      >mdi-window-minimize</v-icon>
    </div>
    <div
      class="background"
      :style="{ backgroundColor: options.theme.backgroundColor, height: `${height - 28}px` }"
    >
      <div
        class="resize bottom"
        :style="{ backgroundColor: options.theme.borderColor }"
        @mousedown.prevent="ev => startResize(ev, 'bottom')"
      ></div>
      <div
        class="resize left"
        :style="{ backgroundColor: options.theme.borderColor }"
        @mousedown.prevent="ev => startResize(ev, 'left')"
      ></div>
      <div
        class="resize right"
        :style="{ backgroundColor: options.theme.borderColor }"
        @mousedown.prevent="ev => startResize(ev, 'right')"
      ></div>
      <iframe
        ref="frame"
        class="view"
        :style="{ pointerEvents: (iframeCapturesEvents) ? 'auto' : 'none'}"
        :src="src"
      ></iframe>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: "Window",

  props: {
    title: {
      type: String,
      default: "Window",
    },
    src: {
      type: URL,
      default: null,
    },
    initialWidth: {
      type: Number,
      default: 800,
    },
    initialHeight: {
      type: Number,
      default: 400,
    },
    initialX: {
      type: Number,
      default: 0,
    },
    initialY: {
      type: Number,
      default: 0,
    },
    focused: {
      type: Boolean,
      default: false,
    },
  },

  data()  {
    return {
      x: this.initialX,
      y: this.initialY,
      width: this.initialWidth,
      height: this.initialHeight,
      action: {
        dragging: false,
        resizing: false,
        direction: null,
        mouseX: null,
        mouseY: null,
      }
    };
  },

  computed: {
    ...mapGetters({
      options: 'options/options',
    }),

    iframeCapturesEvents() {
      if (this.action.resizing || this.action.dragging) {
        return false;
      }
      return this.focused;
    },
  },

  methods: {
    startDrag(ev) {
      this.action.dragging = true;
      this.action.mouseX = ev.clientX;
      this.action.mouseY = ev.clientY;
      window.addEventListener("mousemove", this.drag);
      window.addEventListener("mouseup", this.stopDrag, { once: true });
    },

    startResize(ev, edge) {
      this.action.resizing = true;
      this.action.direction = edge;
      this.action.mouseX = ev.clientX;
      this.action.mouseY = ev.clientY;
      window.addEventListener("mousemove", this.resize);
      window.addEventListener("mouseup", this.stopResize, { once: true });
    },

    drag(ev) {
      const parent = this.$el.parentElement;
      const bounds = parent.getBoundingClientRect()

      let x = this.x, y = this.y;
      x += ev.clientX - this.action.mouseX;
      y += ev.clientY - this.action.mouseY;

      if (y <= 0) {
        return;
      }

      if (ev.clientX <= bounds.left) { // left edge
        return;
      } else if (ev.clientX >= bounds.right) { // right edge
        return;
      } else if (ev.clientY <= bounds.top) { // top edge
        return;
      } else if (ev.clientY >= bounds.bottom) { // bottom edge
        return;      
      }

      this.x = x;
      this.y = y;
      this.action.mouseX = ev.clientX;
      this.action.mouseY = ev.clientY;
    },

    resize(ev) {
      const x = ev.clientX - this.action.mouseX;
      const y = ev.clientY - this.action.mouseY;
      this.action.mouseX = ev.clientX;
      this.action.mouseY = ev.clientY;

      switch (this.action.direction) {
        case "bottom":
          this.height += y;
          break;
        case "left":
          this.x += x;
          this.width -= x;
          break;
        case "right":
          this.width += x;
          break;
      }
    },

    stopDrag(ev) {
      this.action.dragging = false;
      window.removeEventListener("mousemove", this.drag);
    },

    stopResize(ev) {
      this.action.resizing = false;
      this.action.direction = null;
      window.removeEventListener("mousemove", this.resize);
    },
  },
}
</script>

<style scoped>
#window {
  position: absolute;
}

.resize {
  position: absolute;
}

.bottom {
  height: 4px;
  width: 100%;
  left: 0;
  bottom: 0;
  cursor: ns-resize;
}

.left {
  height: 100%;
  width: 4px;
  left: 0;
  bottom: 0;
  cursor: ew-resize;
}

.right {
  height: 100%;
  width: 4px;
  right: 0;
  bottom: 0;
  cursor: ew-resize;
}

.toolbar {
  height: 24px;
  text-align: left;
}

.toolbar-icon {
  cursor: pointer;
  float: right;
  margin: 4px;
}

#title {
  margin: 0px;
  padding-top: 3px;
  padding-left: 4px;
  font-weight: bold;
  color: white;
  overflow: hidden;
  float: left;
}

.background {
  position: absolute;
  width: 100%;
}

.view {
  border: 0px;
  width: 100%;
  height: 100%;
}
</style>
