const CompressionPlugin = require('compression-webpack-plugin');

const VUE_HOST = process.env.VUE_HOST || '0.0.0.0';
const VUE_PORT = parseInt(process.env.VUE_PORT || 8080, 10);

const FLASK_HOST = process.env.FLASK_HOST || 'console-back';
const FLASK_PORT = parseInt(process.env.FLASK_PORT || 8008, 10);

module.exports = {
  outputDir: 'dist/',
  assetsDir: 'assets/',
  devServer: {
    disableHostCheck: true,
    host: VUE_HOST,
    port: VUE_PORT,
    proxy: {
      "^/api/": {
        target: `http://${FLASK_HOST}:${FLASK_PORT}`,
        headers: {
          'Host': `http://${VUE_HOST}:${VUE_PORT}`,
        },
        secure: false
      },
      "^/socket.io/": {
        target: `http://${FLASK_HOST}:${FLASK_PORT}`,
        headers: {
          'Host': `http://${VUE_HOST}:${VUE_PORT}`,
        },
        secure: false,
        ws: true
      },
    },
    watchOptions: {
      ignored: /node_modules/
    },
  },
  transpileDependencies: [
    'vuetify'
  ],
  configureWebpack: {
    plugins: [new CompressionPlugin()],
  }
}
