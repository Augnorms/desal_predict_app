<script setup lang="ts">
import Sidebar from './components/layout/Sidebar.vue'
import TopHeader from './components/layout/TopHeader.vue'
</script>

<template>
  <div class="flex h-screen w-screen overflow-hidden bg-slate-100 font-sans">
    <!-- Left Navigation Sidebar -->
    <Sidebar />

    <!-- Right Main Content Shell -->
    <div class="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
      <!-- Top Header Bar -->
      <TopHeader />

      <!-- Main View Area with Scroll -->
      <main class="flex-1 overflow-y-auto p-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
