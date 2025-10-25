<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1 class="logo" @click="goHome">🎉 抽奖管理系统</h1>
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
    },
    goHome() {
      this.$router.push('/')
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
/* 现代简约全局样式 - 平衡设计 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f5f5;
  min-height: 100vh;
  color: #262626;
}

/* 导航栏 */
.el-header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #262626;
}

.logo {
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.logo:hover {
  color: #1890ff;
  transform: scale(1.02);
}

/* 菜单样式 */
.el-menu {
  background: transparent !important;
  border: none !important;
}

.el-menu-item {
  font-weight: 400;
  font-size: 14px;
  color: #595959 !important;
  transition: all 0.3s;
  border-radius: 4px;
  margin: 0 4px;
  padding: 0 16px;
}

.el-menu-item:hover {
  background: #f5f5f5 !important;
  color: #262626 !important;
}

.el-menu-item.is-active {
  background: #e6f7ff !important;
  color: #1890ff !important;
  border: none !important;
}

/* 主内容区 */
.el-main {
  padding: 0;
  background: #f5f5f5;
  min-height: calc(100vh - 60px);
}

/* 全局卡片样式 */
.el-card {
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: all 0.3s;
}

.el-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.el-card__header {
  border-bottom: 1px solid #e8e8e8;
  padding: 16px 24px;
  background: #fafafa;
  font-weight: 500;
  font-size: 16px;
}

.el-card__body {
  padding: 24px;
}

/* 按钮样式 */
.el-button {
  border-radius: 4px;
  font-weight: 400;
  font-size: 14px;
  transition: all 0.3s;
}

.el-button--primary {
  background: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.el-button--primary:hover {
  background: #40a9ff;
  border-color: #40a9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(24,144,255,0.3);
}

.el-button--default:hover {
  border-color: #1890ff;
  color: #1890ff;
}

/* 表格样式 */
.el-table {
  font-size: 14px;
  border-radius: 8px;
  overflow: hidden;
}

.el-table th {
  background: #fafafa;
  color: #595959;
  font-weight: 500;
  border-bottom: 1px solid #e8e8e8;
}

.el-table td {
  border-bottom: 1px solid #f0f0f0;
}

.el-table tr:hover > td {
  background: #fafafa;
}

/* 标签样式 */
.el-tag {
  border-radius: 4px;
  border: 1px solid currentColor;
  padding: 0 8px;
  font-size: 12px;
}

.el-tag--success {
  background: #f6ffed;
  border-color: #b7eb8f;
  color: #52c41a;
}

.el-tag--info {
  background: #f0f0f0;
  border-color: #d9d9d9;
  color: #595959;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f5f5f5;
}

::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}

/* 输入框样式 */
.el-input__wrapper {
  border-radius: 4px;
  box-shadow: 0 0 0 1px #d9d9d9 inset;
  transition: all 0.3s;
}

.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px #40a9ff inset;
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px #1890ff inset, 0 0 0 3px rgba(24,144,255,0.1);
}

/* 表单样式 */
.el-form-item__label {
  color: #595959;
  font-weight: 500;
}

/* 日期选择器 */
.el-date-editor {
  border-radius: 4px;
}

/* 页面过渡效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.el-main > * {
  animation: fadeIn 0.4s ease-out;
}
</style>
