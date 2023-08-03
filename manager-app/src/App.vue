<template>
  <div>
    <!-- 侧边栏菜单 -->
    <div :class="['sidebar', { 'active': showSidebar }]">
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/about">关于</router-link>
        <router-link to="/list">订阅列表</router-link>
      </nav>
    </div>

    <!-- 主要内容 -->
    <div :class="['main-content', { 'shift-right': showSidebar }]">
      <!-- 汉堡按钮 -->
      <button @click="showSidebar = !showSidebar" class="hamburger-btn">
        <span></span>
        <span></span>
        <span></span>
      </button>

      <router-view/>
    </div>
  </div>
</template>

<style>
/* 样式请根据需要自行调整 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

.hamburger-btn {
  display: block;
  cursor: pointer;
  background-color: transparent;
  border: none;
  padding: 5px;
}

.hamburger-btn span {
  display: block;
  width: 30px;
  height: 3px;
  background-color: #2c3e50;
  margin-bottom: 5px;
}

.sidebar {
  position: fixed;
  top: 0;
  left: -200px; /* 隐藏侧边栏 */
  height: 100%;
  width: 200px;
  background-color: #f0f0f0;
  z-index: 998;
  transition: left 0.3s ease;
}

.sidebar.active {
  left: 0; /* 显示侧边栏 */
}

nav {
  padding: 30px;
  display: flex;
  flex-direction: column; /* 垂直排列 */
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 15px; /* 调整导航按钮之间的间距 */
}

nav a.router-link-exact-active {
  color: #42b983;
}

.main-content {
  margin-left: 0; /* 初始不偏移 */
  padding: 30px;
  transition: margin-left 0.3s ease;
}

.main-content.shift-right {
  margin-left: 200px; /* 侧边栏的宽度 */
}
</style>

<script setup>
import { ref } from 'vue';

const showSidebar = ref(false);
</script>
