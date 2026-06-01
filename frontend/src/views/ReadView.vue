<script setup lang="ts">
import { NButton, NCard, NEmpty, NIcon, NTag } from "naive-ui";
import { DocumentTextOutline, PhonePortraitOutline, ScanOutline } from "@vicons/ionicons5";
import { computed } from "vue";

import { useNfcStore } from "../stores/nfc";

const store = useNfcStore();
const hasRecords = computed(() => (store.tag?.records.length ?? 0) > 0);
</script>

<template>
  <div class="read-view">
    <header class="page-header">
      <h1 class="page-title">读取标签</h1>
      <p class="page-subtitle">扫描并解析 NFC 标签中的 NDEF 记录</p>
    </header>

    <div class="action-bar fade-up">
      <NButton type="primary" size="large" :loading="store.busy" :disabled="!store.connectedReader" @click="store.readTag">
        <template #icon><NIcon><ScanOutline /></NIcon></template>
        读取标签
      </NButton>
      <span v-if="!store.connectedReader" class="warning-hint">请先在仪表盘连接读写器</span>
    </div>

    <Transition name="slide-fade" mode="out-in">
      <div v-if="store.tag" key="has-tag" class="tag-content">
        <NCard class="meta-card fade-up" style="animation-delay: 80ms">
          <div class="meta-grid">
            <div class="meta-item">
              <span class="meta-label">UID</span>
              <code class="meta-value uid">{{ store.tag.uid }}</code>
            </div>
            <div class="meta-item">
              <span class="meta-label">记录数</span>
              <span class="meta-value">{{ store.tag.records.length }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">状态</span>
              <NTag type="success" size="small" round :bordered="false">已读取</NTag>
            </div>
          </div>
        </NCard>

        <NCard title="NDEF 记录" class="records-card fade-up" style="animation-delay: 160ms">
          <template #header-extra><NIcon :size="18" class="text-muted"><DocumentTextOutline /></NIcon></template>
          <TransitionGroup name="list" tag="div" class="records-list">
            <div v-for="(record, index) in store.tag.records" :key="index" class="record-block">
              <div class="record-header">
                <NTag size="small" :bordered="false" round>#{{ index + 1 }}</NTag>
                <span class="record-type">Text</span>
              </div>
              <div class="record-body"><pre class="record-content">{{ record }}</pre></div>
            </div>
          </TransitionGroup>
          <NEmpty v-if="!hasRecords" description="标签中无 NDEF 记录" />
        </NCard>
      </div>

      <div v-else key="no-tag" class="empty-state fade-up">
        <div class="scan-animation">
          <div class="scan-ring sr1" />
          <div class="scan-ring sr2" />
          <div class="scan-icon"><NIcon :size="40" color="var(--color-primary)"><PhonePortraitOutline /></NIcon></div>
        </div>
        <p class="empty-text">等待读取标签…</p>
        <p class="empty-hint">将 NFC 标签放置在读写器上，然后点击"读取标签"</p>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.read-view { max-width: 720px; }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text); letter-spacing: -0.5px; }
.page-subtitle { margin-top: 4px; font-size: 14px; color: var(--color-text-secondary); }
.text-muted { color: var(--color-text-muted); }
.action-bar { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.warning-hint { font-size: 13px; color: var(--color-warning); }
.tag-content { display: flex; flex-direction: column; gap: 16px; }
.meta-card, .records-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); }
.meta-grid { display: flex; align-items: center; gap: 32px; }
.meta-item { display: flex; flex-direction: column; gap: 4px; }
.meta-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--color-text-muted); }
.meta-value { font-size: 15px; font-weight: 600; color: var(--color-text); }
.meta-value.uid { font-family: "JetBrains Mono", monospace; color: var(--color-primary); letter-spacing: 1px; }
.records-list { display: flex; flex-direction: column; gap: 10px; }
.record-block { background: var(--color-bg); border: 1px solid var(--color-border); border-radius: var(--radius-sm); overflow: hidden; transition: border-color var(--transition-fast); }
.record-block:hover { border-color: var(--color-border-hover); }
.record-header { display: flex; align-items: center; gap: 10px; padding: 10px 16px; border-bottom: 1px solid var(--color-border); }
.record-type { font-size: 12px; color: var(--color-text-muted); }
.record-body { padding: 14px 16px; }
.record-content { font-family: "JetBrains Mono", monospace; font-size: 13px; color: var(--color-text); white-space: pre-wrap; word-break: break-all; margin: 0; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 20px; text-align: center; }
.scan-animation { position: relative; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; margin-bottom: 24px; }
.scan-icon { z-index: 1; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.scan-ring { position: absolute; border-radius: 50%; border: 2px solid var(--color-primary); animation: scan-pulse 2.5s ease-in-out infinite; }
.sr1 { width: 70px; height: 70px; animation-delay: 0s; }
.sr2 { width: 100px; height: 100px; animation-delay: 0.8s; }
@keyframes scan-pulse { 0% { transform: scale(0.8); opacity: 0.5; } 50% { transform: scale(1.1); opacity: 0.12; } 100% { transform: scale(0.8); opacity: 0.5; } }
.empty-text { font-size: 16px; font-weight: 600; color: var(--color-text); margin-bottom: 6px; }
.empty-hint { font-size: 13px; color: var(--color-text-muted); }
.fade-up { animation: fade-up-in 0.5s cubic-bezier(0.4, 0, 0.2, 1) both; }
@keyframes fade-up-in { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.slide-fade-enter-active { transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-fade-leave-active { transition: all 200ms ease; }
.slide-fade-enter-from { opacity: 0; transform: translateY(20px); }
.slide-fade-leave-to { opacity: 0; transform: translateY(-10px); }
.list-enter-active { transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.list-leave-active { transition: all 200ms ease; }
.list-enter-from { opacity: 0; transform: translateX(-20px); }
.list-leave-to { opacity: 0; transform: translateX(20px); }
</style>
