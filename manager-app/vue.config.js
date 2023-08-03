const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
})

module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Flask后端的地址
        changeOrigin: true,
        // pathRewrite: {
        //   '^/api': '', // 将/api重写，使请求路径符合后端定义的路由
        // },
      },
    },
  },
};
