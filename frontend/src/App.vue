<script setup lang="ts">
import {
  NConfigProvider,
  NDialogProvider,
  NIcon,
  NMessageProvider,
} from "naive-ui";
import {
  CardOutline,
  HardwareChipOutline,
  ReaderOutline,
  TimeOutline,
} from "@vicons/ionicons5";
import { ref } from "vue";

import DashboardView from "./views/DashboardView.vue";
import HistoryView from "./views/HistoryView.vue";
import ReadView from "./views/ReadView.vue";
import WriteView from "./views/WriteView.vue";

type Page = "dashboard" | "read" | "write" | "history";

const activePage = ref<Page>("dashboard");

const menuOptions = [
  { label: "仪表盘", key: "dashboard", icon: HardwareChipOutline },
  { label: "读取", key: "read", icon: ReaderOutline },
  { label: "写入", key: "write", icon: CardOutline },
  { label: "历史", key: "history", icon: TimeOutline },
];

function handleMenuSelect(key: string) {
  activePage.value = key as Page;
}
</script>

<template>
  <NConfigProvider>
    <NMessageProvider>
      <NDialogProvider>
        <div class="app-layout">
          <!-- 侧边导航栏 -->
          <aside class="sidebar">
            <div class="sidebar-brand">
              <img class="brand-icon" src="/logo.png" alt="NFC Writer" />
              <span class="brand-text">NFC Writer</span>
            </div>

            <nav class="sidebar-nav">
              <button
                v-for="item in menuOptions"
                :key="item.key"
                class="nav-item"
                :class="{ active: activePage === item.key }"
                @click="handleMenuSelect(item.key)"
              >
                <NIcon :size="20" class="nav-icon">
                  <component :is="item.icon" />
                </NIcon>
                <span class="nav-label">{{ item.label }}</span>
                <div class="nav-indicator" />
              </button>
            </nav>

            <div class="sidebar-footer">
              <span class="version">v0.1.0</span>
            </div>
          </aside>

          <!-- 主内容区 -->
          <main class="main-content">
            <Transition name="page" mode="out-in">
              <DashboardView v-if="activePage === 'dashboard'" key="dashboard" />
              <ReadView v-else-if="activePage === 'read'" key="read" />
              <WriteView v-else-if="activePage === 'write'" key="write" />
              <HistoryView v-else-if="activePage === 'history'" key="history" />
            </Transition>
          </main>
        </div>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
/* ── 全局重置 ── */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body,
#app {
  height: 100%;
  overflow: hidden;
}

body {
  font-family: "Plus Jakarta Sans", "SF Pro Display", -apple-system,
    BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei UI", sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
}

/* ── 布局 ── */
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ── 侧边栏 ── */
.sidebar {
  width: 224px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  padding: 24px 12px;
  user-select: none;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 12px 28px;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  object-fit: cover;
}

.brand-text {
  font-weight: 700;
  font-size: 15px;
  color: var(--color-text);
  letter-spacing: -0.3px;
}

/* ── 导航项 ── */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  overflow: hidden;
}

.nav-item:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.nav-icon {
  transition: transform var(--transition-fast);
}

.nav-item:hover .nav-icon {
  transform: scale(1.1);
}

.nav-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) scaleY(0);
  width: 3px;
  height: 18px;
  border-radius: 0 3px 3px 0;
  background: var(--color-primary);
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.nav-item.active .nav-indicator {
  transform: translateY(-50%) scaleY(1);
}

/* ── 侧边栏底部 ── */
.sidebar-footer {
  padding: 12px 12px 0;
  border-top: 1px solid var(--color-border);
}

.version {
  font-size: 11px;
  color: var(--color-text-muted);
}

/* ── 主内容 ── */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 32px 40px;
  background: var(--color-bg);
}

/* ── 页面切换动画 ── */
.page-enter-active {
  transition: all var(--transition-slow);
}

.page-leave-active {
  transition: all 200ms ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── 滚动条 ── */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-hover);
}
</style>
