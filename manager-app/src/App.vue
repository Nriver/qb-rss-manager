<template>
  <div>
    <!-- 侧边栏菜单 -->
    <div :class="['sidebar', { 'active': showSidebar }]">
      <!-- Logo图片 -->
      <div class="center-logo">
        <img src="~@/assets/logo.png" alt="Logo" />
      </div>

      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/list">订阅列表</router-link>
        <router-link to="/config">设置</router-link>
        <router-link to="/configEditor">编辑配置文件</router-link>
        <router-link to="/about">关于</router-link>
      </nav>
    </div>

    <!-- 主要内容 -->
    <div :class="['main-content', { 'shift-right': showSidebar }]">
      <div class="header">
        <div class="left">
          <!-- 汉堡按钮 -->
          <button @click="showSidebar = !showSidebar" class="hamburger-btn">
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>

        <!-- 显示当前路由名称 -->
        <div class="current-route center">{{ $route.name }}</div>
      </div>

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

.header {
  display: flex;
  align-items: center; /* 垂直居中对齐 */
  margin-bottom: 10px;
}

.hamburger-btn {
  display: block;
  cursor: pointer;
  background-color: transparent;
  border: none;
  padding: 5px;
  margin-right: 10px; /* 设置汉堡按钮和当前路由名称的间距 */
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

.current-route {
  font-weight: bold;
  color: #2c3e50;
  font-size: 2em;
  margin-right: 2em;
}

.left {
  /* 设置按钮区域占据的空间 */
  flex: 0 0 auto;
  /* 可选：设置按钮与文字之间的间距 */
  margin-right: 10px;
}

.center {
  /* 设置文字区域占据的空间，剩余空间将用于文字居中 */
  flex: 1;
  text-align: center;
}

.center-logo {
  margin-top: 2em;
  /* 设置Logo区域占据的空间，剩余空间将用于Logo居中 */
  flex: 1;
  display: flex;
  justify-content: center; /* 居中显示Logo图片 */
}

.center-logo img {
  /* 可以根据需要调整Logo图片的样式，如宽度、高度等 */
  max-width: 100%;
  max-height: 100px;
}

</style>

<script setup>
import { ref } from 'vue';

const showSidebar = ref(false);
</script>
