module.exports = {
  devServer: {
    port: 8080,
    host: '0.0.0.0',  // 允许外部访问
    proxy: {
      '/api': {
        target: 'http://192.168.10.23:8000',  // 改为局域网IP
        changeOrigin: true
      }
    },
    headers: {
      'Cache-Control': 'no-store'  // 禁用缓存，确保总是获取最新代码
    }
  },
  // 添加文件哈希，强制浏览器更新
  filenameHashing: true
}
