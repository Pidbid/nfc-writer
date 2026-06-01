<script setup lang="ts">
import {
  NButton,
  NCard,
  NIcon,
  NSpace,
  NTag,
} from "naive-ui";
import {
  BluetoothOutline,
  HardwareChipOutline,
  RadioOutline,
  ReaderOutline,
  ScanOutline,
} from "@vicons/ionicons5";
import { computed } from "vue";

import { useNfc } from "../composables/useNfc";

const { status, connectedReader, tag, readers, busy, connect, disconnect, readTag } = useNfc();

const statusColor = computed(() => connectedReader.value ? "var(--color-success)" : "var(--color-text-muted)");
const statusText = computed(() => connectedReader.value ? "已连接" : "未连接");

const cardDelay = (i: number) => ({ animationDelay: `${i * 80}ms` });
</script>

<template>
  <div class="dashboard">
    <header class="page-header">
      <h1 class="page-title">仪表盘</h1>
      <p class="page-subtitle">NFC 读写器状态概览</p>
    </header>

    <!-- 状态卡片行 -->
    <div class="status-grid">
      <div class="stat-card fade-up" :style="cardDelay(0)">
        <div class="stat-icon" :style="{ background: connectedReader ? '#16a34a10' : '#94a3b810', color: statusColor }">
          <NIcon :size="22"><RadioOutline /></NIcon>
        </div>
        <div class="stat-body">
          <span class="stat-label">读写器状态</span>
          <span class="stat-value">{{ statusText }}</span>
        </div>
      </div>

      <div class="stat-card fade-up" :style="cardDelay(1)">
        <div class="stat-icon blue">
          <NIcon :size="22"><BluetoothOutline /></NIcon>
        </div>
        <div class="stat-body">
          <span class="stat-label">适配器</span>
          <span class="stat-value">{{ status.adapter }}</span>
        </div>
      </div>

      <div class="stat-card fade-up" :style="cardDelay(2)">
        <div class="stat-icon amber">
          <NIcon :size="22"><HardwareChipOutline /></NIcon>
        </div>
        <div class="stat-body">
          <span class="stat-label">已发现读写器</span>
          <span class="stat-value">{{ readers.length }}</span>
        </div>
      </div>

      <div class="stat-card fade-up" :style="cardDelay(3)">
        <div class="stat-icon rose">
          <NIcon :size="22"><ReaderOutline /></NIcon>
        </div>
        <div class="stat-body">
          <span class="stat-label">标签记录</span>
          <span class="stat-value">{{ tag?.records.length ?? 0 }}</span>
        </div>
      </div>
    </div>

    <!-- 读写器列表 -->
    <Transition name="fade-up" appear>
      <NCard title="可用读写器" class="section-card">
        <template #header-extra>
          <NButton size="small" quaternary :loading="busy">
            刷新
          </NButton>
        </template>

        <TransitionGroup name="list" tag="div" class="reader-list">
          <div
            v-for="reader in readers"
            :key="reader.id"
            class="reader-item"
            :class="{ connected: reader.connected }"
          >
            <div class="reader-info">
              <NIcon :size="18" class="reader-icon">
                <HardwareChipOutline />
              </NIcon>
              <div>
                <span class="reader-name">{{ reader.name }}</span>
                <span class="reader-id">{{ reader.id }}</span>
              </div>
            </div>
            <NSpace size="small">
              <NTag
                v-if="reader.connected"
                type="success"
                size="small"
                round
                :bordered="false"
              >
                已连接
              </NTag>
              <NButton
                v-if="reader.connected"
                size="small"
                tertiary
                type="error"
                :disabled="busy"
                @click="disconnect"
              >
                断开
              </NButton>
              <NButton
                v-else
                size="small"
                tertiary
                type="primary"
                :disabled="busy"
                @click="connect(reader.id)"
              >
                连接
              </NButton>
            </NSpace>
          </div>
        </TransitionGroup>

        <div v-if="readers.length === 0" class="empty-hint">
          未检测到 NFC 读写器
        </div>
      </NCard>
    </Transition>

    <!-- 快速读取 -->
    <Transition name="fade-up" appear>
      <NCard title="快速读取" class="section-card" style="animation-delay: 200ms">
        <div class="quick-read">
          <div class="tag-preview">
            <Transition name="scale" mode="out-in">
              <div v-if="tag" key="tag-data" class="tag-data">
                <div class="tag-uid">
                  <span class="uid-label">UID</span>
                  <code class="uid-value">{{ tag.uid }}</code>
                </div>
                <div class="tag-records">
                  <div v-for="(record, i) in tag.records" :key="i" class="record-item">
                    <span class="record-index">#{{ i + 1 }}</span>
                    <span class="record-text">{{ record }}</span>
                  </div>
                </div>
              </div>
              <div v-else key="no-tag" class="no-tag">
                <div class="nfc-ripple">
                  <div class="ripple r1" />
                  <div class="ripple r2" />
                  <div class="ripple r3" />
                  <div class="nfc-core">
                    <NIcon :size="28" color="#ffffff"><ScanOutline /></NIcon>
                  </div>
                </div>
                <span class="hint-text">请将 NFC 标签靠近读写器</span>
              </div>
            </Transition>
          </div>
          <NButton
            type="primary"
            size="large"
            :loading="busy"
            :disabled="!connectedReader"
            @click="readTag"
          >
            <template #icon>
              <NIcon><ScanOutline /></NIcon>
            </template>
            读取标签
          </NButton>
        </div>
      </NCard>
    </Transition>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 920px;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.5px;
}

.page-subtitle {
  margin-top: 4px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

/* ── 状态网格 ── */
.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-normal), transform var(--transition-fast), box-shadow var(--transition-normal);
}

.stat-card:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.stat-icon.blue { background: #2563eb10; color: var(--color-primary); }
.stat-icon.amber { background: #f59e0b10; color: #f59e0b; }
.stat-icon.rose { background: #e11d4810; color: #e11d48; }

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-muted);
  font-weight: 500;
}

.stat-value {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text);
}

/* ── 卡片 ── */
.section-card {
  margin-bottom: 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

/* ── 读写器列表 ── */
.reader-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reader-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), background var(--transition-fast);
  cursor: pointer;
}

.reader-item:hover {
  border-color: var(--color-border-hover);
}

.reader-item.connected {
  border-color: #16a34a30;
  background: #16a34a06;
}

.reader-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reader-icon {
  color: var(--color-text-muted);
}

.reader-item.connected .reader-icon {
  color: var(--color-success);
}

.reader-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-text);
  display: block;
}

.reader-id {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: "JetBrains Mono", monospace;
}

.empty-hint {
  text-align: center;
  padding: 32px;
  color: var(--color-text-muted);
  font-size: 14px;
}

/* ── 快速读取 ── */
.quick-read {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 16px 0;
}

.tag-preview {
  width: 100%;
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-data {
  width: 100%;
}

.tag-uid {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.uid-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-primary);
  background: var(--color-primary-bg);
  padding: 3px 8px;
  border-radius: 6px;
}

.uid-value {
  font-family: "JetBrains Mono", monospace;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: 1px;
}

.tag-records {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}

.record-index {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-primary-bg);
  padding: 2px 7px;
  border-radius: 5px;
  flex-shrink: 0;
}

.record-text {
  font-size: 13px;
  color: var(--color-text);
  word-break: break-all;
}

/* ── NFC 波纹动画 ── */
.no-tag {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.nfc-ripple {
  position: relative;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nfc-core {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), #16a34a);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.ripple {
  position: absolute;
  border-radius: 50%;
  border: 2px solid var(--color-primary);
  opacity: 0;
  animation: ripple-out 3s ease-out infinite;
}

.r1 { width: 70px; height: 70px; animation-delay: 0s; }
.r2 { width: 85px; height: 85px; animation-delay: 0.6s; }
.r3 { width: 100px; height: 100px; animation-delay: 1.2s; }

@keyframes ripple-out {
  0% { transform: scale(0.6); opacity: 0.35; }
  100% { transform: scale(1.2); opacity: 0; }
}

.hint-text {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* ── 列表动画 ── */
.list-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.list-leave-active {
  transition: all 200ms ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-16px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(16px);
}

/* ── 淡入上移动画 ── */
.fade-up {
  animation: fade-up-in 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes fade-up-in {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── 缩放过渡 ── */
.scale-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.scale-leave-active {
  transition: all 200ms ease;
}

.scale-enter-from {
  opacity: 0;
  transform: scale(0.92);
}

.scale-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
</style>
