<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🎉 抽奖管理系统</h1>
          <el-menu
            :default-active="activeIndex"
            mode="horizontal"
            @select="handleSelect"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/lotteries">抽奖列表</el-menu-item>
            <el-menu-item index="/create">创建抽奖</el-menu-item>
            <el-menu-item index="/statistics">数据统计</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      activeIndex: '/'
    }
  },
  methods: {
    handleSelect(key) {
      this.$router.push(key)
    }
  },
  watch: {
    '$route.path': {
      immediate: true,
      handler(newPath) {
        this.activeIndex = newPath
      }
    }
  }
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.el-header {
  background-color: #409EFF;
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
}

.el-main {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}
</style>
