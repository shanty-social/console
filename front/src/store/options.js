import config from '@/config.json';

const defaults = {
    wallpaperIndex: 1,
    themeIndex: 0,
}

let options = localStorage.getItem("options");

if (options) {
    try {
        options = JSON.parse(options);
    } catch (e) {
        options = null;
    }
}
if (!options) {
    options = defaults;
}

export default {
  namespaced: true,

  state: {
    options: {
        ...options,
        theme: config.themes[options.themeIndex],
        wallpaper: config.wallpapers[options.wallpaperIndex],
    },
  },

  getters: {
    options (state) {
      return state.options
    },
  },

  mutations: {
  },

  actions: {
  }
}
