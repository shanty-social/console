<template>
  <div>
    <div
      class="preview-container"
      :title="`Preview of ${previewUrl}`"
    >
      <img
        v-if="!preview"
        class="preview-notfound"
        src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/PjwhRE9DVFlQRSBzdmcgIFBVQkxJQyAnLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4nICAnaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkJz48c3ZnIGVuYWJsZS1iYWNrZ3JvdW5kPSJuZXcgMCAwIDMyIDMyIiBoZWlnaHQ9IjMycHgiIGlkPSJMYXllcl8xIiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAzMiAzMiIgd2lkdGg9IjMycHgiIHhtbDpzcGFjZT0icHJlc2VydmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPjxnIGlkPSJwaG90b18xXyI+PHBhdGggZD0iTTI3LDBINUMyLjc5MSwwLDEsMS43OTEsMSw0djI0YzAsMi4yMDksMS43OTEsNCw0LDRoMjJjMi4yMDksMCw0LTEuNzkxLDQtNFY0QzMxLDEuNzkxLDI5LjIwOSwwLDI3LDB6ICAgIE0yOSwyOGMwLDEuMTAyLTAuODk4LDItMiwySDVjLTEuMTAzLDAtMi0wLjg5OC0yLTJWNGMwLTEuMTAzLDAuODk3LTIsMi0yaDIyYzEuMTAyLDAsMiwwLjg5NywyLDJWMjh6IiBmaWxsPSIjMzMzMzMzIi8+PHBhdGggZD0iTTI2LDRINkM1LjQ0Nyw0LDUsNC40NDcsNSw1djE4YzAsMC41NTMsMC40NDcsMSwxLDFoMjBjMC41NTMsMCwxLTAuNDQ3LDEtMVY1QzI3LDQuNDQ3LDI2LjU1Myw0LDI2LDR6ICAgIE0yNiw1djEzLjg2OWwtMy4yNS0zLjUzQzIyLjU1OSwxNS4xMjMsMjIuMjg3LDE1LDIyLDE1cy0wLjU2MSwwLjEyMy0wLjc1LDAuMzM5bC0yLjYwNCwyLjk1bC03Ljg5Ni04Ljk1ICAgQzEwLjU2LDkuMTIzLDEwLjI4Nyw5LDEwLDlTOS40NCw5LjEyMyw5LjI1LDkuMzM5TDYsMTMuMDg3VjVIMjZ6IE02LDE0LjZsNC00LjZsOC4wNjYsOS4xNDNsMC41OCwwLjY1OEwyMS40MDgsMjNINlYxNC42eiAgICBNMjIuNzQsMjNsLTMuNDI4LTMuOTU1TDIyLDE2bDQsNC4zNzlWMjNIMjIuNzR6IiBmaWxsPSIjMzMzMzMzIi8+PHBhdGggZD0iTTIwLDEzYzEuNjU2LDAsMy0xLjM0MywzLTNzLTEuMzQ0LTMtMy0zYy0xLjY1OCwwLTMsMS4zNDMtMywzUzE4LjM0MiwxMywyMCwxM3ogTTIwLDhjMS4xMDIsMCwyLDAuODk3LDIsMiAgIHMtMC44OTgsMi0yLDJjLTEuMTA0LDAtMi0wLjg5Ny0yLTJTMTguODk2LDgsMjAsOHoiIGZpbGw9IiMzMzMzMzMiLz48L2c+PC9zdmc+"
      />
      <div
        class="preview"
      >
        <iframe
          v-if="preview"
          :src="previewUrl"
          frameborder="0"
          onload="this.style.opacity = 1"
        ></iframe>
      </div>
    </div>
    <v-select
      label="Protocol"
      v-model="protocol"
      :items="['http://', 'https://']"
    ></v-select>
    <v-select
      label="Hostname"
      v-model="hostname"
      :items="this.hostnames"
    ></v-select>
    <v-combobox
      label="Port"
      v-model="port"
      :items="this.value.ports"
    ></v-combobox>
    <v-text-field
      v-model="path"
      label="Path"
    ></v-text-field>
  </div>
</template>

<script>
import axios from 'axios'

function isUrlValid(s) {
  try {
    new URL(s)
    return true
  } catch (e) {
    return false
  }
}

export default {
  name: 'HostPreview',

  props: {
    value: Object,
  },

  data() {
    const hostnames = []
    hostnames.push(...this.value.addresses)
    hostnames.push(...this.value.aliases)
    hostnames.push(this.value.hostname)

    const defaultPort = this.value.default_port || this.value.ports[0]

    return {
      protocol: 'http://',
      hostname: (hostnames.length) ? hostnames[0] : null,
      port: defaultPort,
      path: '/',
      preview: false,
    }
  },

  computed: {
    hostnames() {
      const hostnames = []
      hostnames.push(...this.value.addresses)
      hostnames.push(...this.value.aliases)
      hostnames.push(this.value.hostname)
      return hostnames
    },

    previewUrl() {
      return `${this.protocol}${this.hostname}:${this.port}${this.path}`
    },
  },

  mounted() {
    this.checkUrl()
  },

  watch: {
    previewUrl() {
      this.checkUrl()
    },
  },

  methods: {
    checkUrl() {
      let url = this.previewUrl

      this.preview = false;

      if (!isUrlValid(url)) {
        return
      }

      axios
        .get(`/api/hosts/head/`, { params: { url: url }})
        .then(() => {
          this.preview = true
        })
    },
  },
}
</script>

<style scoped>
.preview iframe {
  width: 800px;
  height: 600px;
  opacity: 0;
  transition: all 300ms ease-in-out;
}

.preview {
  -ms-zoom: 0.4;
  -moz-transform: scale(0.4);
  -moz-transform-origin: 0 0;
  -o-transform: scale(0.4);
  -o-transform-origin: 0 0;
  -webkit-transform: scale(0.4);
  -webkit-transform-origin: 0 0;
}

.preview:after {
  content: "";
  display: block;
  position: absolute;
  width: 800px;
  height: 600px;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.preview-container {
  height: calc(600px * 0.4);
  width: 100%;
  display: inline-block;
  overflow: hidden;
  position: relative;
  background: #f0f0f0;
}

.preview-notfound {
  position: absolute;
  left: calc(50% - 16px);
  top: calc(50% - 18px);
  opacity: 0.2;
  display: block;
  -ms-zoom: 2;
  -o-transform: scale(2);
  -moz-transform: scale(2);
  -webkit-transform: scale(2);
}
</style>
