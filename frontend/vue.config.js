const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: '/',
  assetsDir: 'static', // 静态资源目录
  pwa: {
    iconPaths: {
      favicon32: "./favicon.ico",
      favicon16: "./favicon.ico",
      favicon64: '/favicon.ico'
    }
  },
})
