<script setup lang="ts">
import { NCard, NEmpty, NIcon, NTag, NTime } from "naive-ui";
import {
  CheckmarkCircleOutline,
  CreateOutline,
  LinkOutline,
  LogOutOutline,
  ReaderOutline,
  TimeOutline,
} from "@vicons/ionicons5";
import { computed, ref, type Component } from "vue";

import { useNfcStore } from "../stores/nfc";
import type { HistoryEntry } from "../stores/nfc";

const store = useNfcStore();
const filter = ref<"all" | HistoryEntry["action"]>("all");

const filtered = computed(() => {
  if (filter.value === "all") return store.history;
  return store.history.filter((e) => e.action === filter.value);
});

const actionMeta: Record<HistoryEntry["action"], { label: string; icon: Component; color: string }> = {
  read: { label: "读取", icon: ReaderOutline, color: "#2563eb" },
  write: { label: "写入", icon: CreateOutline, color: "#16a34a" },
  connect: { label: "连接", icon: LinkOutline, color: "#7c3aed" },
  disconnect: { label: "断开", icon: LogOutOutline, color: "#f59e0b" },
};

const filters = [
  { key: "all", label: "全部" },
  { key: "read", label: "读取" },
  { key: "write", label: "写入" },
  { key: "connect", label: "连接" },
  { key: "disconnect", label: "断开" },
] as const;
</script>

<template>
  <div class="history-view">
    <header class="page-header">
      <h1 class="page-title">操作日志</h1>
      <p class="page-subtitle">记录所有 NFC 读写操作</p>
    </header>

    <div class="filter-bar fade-up">
      <button v-for="f in filters" :key="f.key" class="filter-chip" :class="{ active: filter === f.key }" @click="filter = f.key">
        {{ f.label }}
      </button>
    </div>

    <NCard class="log-card fade-up" style="animation-delay: 100ms">
      <template #header-extra><NIcon :size="18" class="text-muted"><TimeOutline /></NIcon></template>
      <TransitionGroup name="list" tag="div" class="log-list">
        <div v-for="(entry, i) in filtered" :key="entry.id" class="log-entry" :style="{ animationDelay: `${i * 40}ms` }">
          <div class="log-icon" :style="{ background: actionMeta[entry.action].color + '12', color: actionMeta[entry.action].color }">
            <NIcon :size="18"><component :is="actionMeta[entry.action].icon" /></NIcon>
          </div>
          <div class="log-body">
            <div class="log-top">
              <NTag :type="entry.success ? 'success' : 'error'" size="tiny" :bordered="false" round>{{ actionMeta[entry.action].label }}</NTag>
              <span class="log-time"><NTime :time="entry.time" format="HH:mm:ss" /></span>
            </div>
            <p class="log-detail">{{ entry.detail }}</p>
          </div>
        </div>
      </TransitionGroup>
      <NEmpty v-if="filtered.length === 0" description="暂无操作记录" />
    </NCard>
  </div>
</template>

<style scoped>
.history-view { max-width: 720px; }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text); letter-spacing: -0.5px; }
.page-subtitle { margin-top: 4px; font-size: 14px; color: var(--color-text-secondary); }
.text-muted { color: var(--color-text-muted); }
.filter-bar { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.filter-chip { padding: 6px 16px; border: 1px solid var(--color-border); border-radius: 20px; background: var(--color-surface); color: var(--color-text-secondary); font-size: 13px; font-weight: 500; cursor: pointer; transition: all var(--transition-normal); }
.filter-chip:hover { border-color: var(--color-border-hover); color: var(--color-text); }
.filter-chip.active { border-color: var(--color-primary); background: var(--color-primary-bg); color: var(--color-primary); }
.log-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); }
.log-list { display: flex; flex-direction: column; gap: 6px; }
.log-entry { display: flex; align-items: flex-start; gap: 14px; padding: 14px 16px; background: var(--color-bg); border: 1px solid var(--color-border); border-radius: var(--radius-md); transition: border-color var(--transition-fast); animation: fade-in 0.3s ease both; }
.log-entry:hover { border-color: var(--color-border-hover); }
.log-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.log-body { flex: 1; min-width: 0; }
.log-top { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.log-time { font-size: 11px; color: var(--color-text-muted); font-family: "JetBrains Mono", monospace; }
.log-detail { font-size: 13px; color: var(--color-text-secondary); line-height: 1.5; word-break: break-all; }
.fade-up { animation: fade-up-in 0.5s cubic-bezier(0.4, 0, 0.2, 1) both; }
@keyframes fade-up-in { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
.list-enter-active { transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.list-leave-active { transition: all 200ms ease; }
.list-enter-from { opacity: 0; transform: translateX(-20px); }
.list-leave-to { opacity: 0; transform: translateX(20px); }
</style>
