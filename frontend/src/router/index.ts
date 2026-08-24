import { createRouter, createWebHashHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import PredictionCenterView from '../views/PredictionCenterView.vue'
import IotPredictiveView from '../views/IotPredictiveView.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView
  },
  {
    path: '/prediction-center',
    name: 'PredictionCenter',
    component: PredictionCenterView
  },
  {
    path: '/iot-predictive-center',
    name: 'IotPredictiveView',
    component: IotPredictiveView
  }
]

export const router = createRouter({
  history: createWebHashHistory(),
  routes
})
