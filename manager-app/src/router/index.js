import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ItemList from "@/components/ItemList.vue";
import Config from "@/components/Config.vue";
import ConfigEditor from "@/components/ConfigEditor.vue";


const routes = [
  {
    path: '/',
    name: '首页',
    component: HomeView
  },
  {
    path: '/about',
    name: '关于',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/list',
    name: '订阅列表',
    component: ItemList
  },
  {
    path: '/config',
    name: '设置',
    component: Config
  },
  {
    path: '/configEditor',
    name: '编辑配置文件',
    component: ConfigEditor
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
