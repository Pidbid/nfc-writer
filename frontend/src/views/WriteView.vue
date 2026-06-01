<script setup lang="ts">
import {
  NButton,
  NCard,
  NIcon,
  NInput,
  NSelect,
  NTooltip,
} from "naive-ui";
import {
  AtOutline,
  CallOutline,
  CreateOutline,
  GlobeOutline,
  InformationCircleOutline,
  LogoWechat,
  PersonOutline,
  TextOutline,
  WifiOutline,
} from "@vicons/ionicons5";
import { computed, ref, type Component } from "vue";

import { useNfcStore } from "../stores/nfc";

const store = useNfcStore();

interface RecordType {
  id: string;
  label: string;
  icon: Component;
  desc: string;
}

const recordTypes: RecordType[] = [
  { id: "text", label: "文本", icon: TextOutline, desc: "纯文本内容" },
  { id: "url", label: "网址", icon: GlobeOutline, desc: "网站链接" },
  { id: "email", label: "邮件", icon: AtOutline, desc: "电子邮件地址" },
  { id: "phone", label: "电话", icon: CallOutline, desc: "电话号码" },
  { id: "wifi", label: "WiFi", icon: WifiOutline, desc: "WiFi 网络配置" },
  { id: "contact", label: "联系人", icon: PersonOutline, desc: "vCard 联系人" },
  { id: "miniprogram", label: "小程序", icon: LogoWechat, desc: "微信小程序 URL Scheme" },
];

const selectedType = ref<RecordType>(recordTypes[0]);
const payload = ref("");
const writeSuccess = ref(false);

// ── 小程序表单 ──
const mpAppid = ref("");
const mpPath = ref("");
const mpQuery = ref("");
const mpEnvVersion = ref<"release" | "trial" | "develop">("release");

const mpEnvOptions = [
  { label: "正式版", value: "release" },
  { label: "体验版", value: "trial" },
  { label: "开发版", value: "develop" },
];

const mpPathError = ref("");
const mpQueryError = ref("");

const mpScheme = computed(() => {
  if (!mpAppid.value || !mpPath.value) return "";
  let scheme = `weixin://dl/business/?appid=${mpAppid.value}&path=${encodeURIComponent(mpPath.value)}`;
  if (mpQuery.value) scheme += `&query=${encodeURIComponent(mpQuery.value)}`;
  if (mpEnvVersion.value !== "release") scheme += `&env_version=${mpEnvVersion.value}`;
  return scheme;
});

const mpPayload = computed(() => mpScheme.value);

function validatePath() {
  mpPathError.value = mpPath.value && !mpPath.value.startsWith("/")
    ? "页面路径应以 / 开头"
    : "";
}

function validateQuery() {
  mpQueryError.value = mpQuery.value.length > 512
    ? `参数过长（${mpQuery.value.length}/512）`
    : "";
}

// ── 通用表单 ──
const formConfig = computed(() => {
  switch (selectedType.value.id) {
    case "text":
      return { type: "textarea" as const, placeholder: "输入要写入的文本…", rows: 4 };
    case "url":
      return { type: "text" as const, placeholder: "https://example.com", rows: 1 };
    case "email":
      return { type: "text" as const, placeholder: "user@example.com", rows: 1 };
    case "phone":
      return { type: "text" as const, placeholder: "+86 138 0000 0000", rows: 1 };
    case "wifi":
      return { type: "text" as const, placeholder: "SSID,密码,加密方式", rows: 1 };
    case "contact":
      return { type: "textarea" as const, placeholder: "姓名\n电话\n邮箱", rows: 3 };
    default:
      return { type: "text" as const, placeholder: "", rows: 1 };
  }
});

const currentPayload = computed(() => {
  if (selectedType.value.id === "miniprogram") return mpPayload.value;
  return payload.value;
});

const canWrite = computed(() => {
  if (!store.connectedReader) return false;
  if (selectedType.value.id === "miniprogram") {
    return mpAppid.value.length > 0 && mpPath.value.length > 0 && !mpPathError.value;
  }
  return payload.value.trim().length > 0;
});

function selectType(type: RecordType) {
  selectedType.value = type;
  payload.value = "";
  writeSuccess.value = false;
}

async function handleWrite() {
  if (!canWrite.value) return;
  const text = currentPayload.value;
  if (!text) return;

  if (selectedType.value.id === "url") {
    await store.writeUri(text);
  } else {
    await store.writeText(text);
  }

  if (!store.error) {
    writeSuccess.value = true;
    setTimeout(() => (writeSuccess.value = false), 2000);
  }
}
</script>

<template>
  <div class="write-view">
    <header class="page-header">
      <h1 class="page-title">写入标签</h1>
      <p class="page-subtitle">选择记录类型并写入 NFC 标签</p>
    </header>

    <!-- 记录类型选择 -->
    <NCard title="记录类型" class="section-card fade-up">
      <template #header-extra>
        <NIcon :size="18" class="text-muted"><CreateOutline /></NIcon>
      </template>

      <div class="type-grid">
        <button
          v-for="(type, i) in recordTypes"
          :key="type.id"
          class="type-card"
          :class="{ selected: selectedType.id === type.id }"
          :style="{ animationDelay: `${i * 50}ms` }"
          @click="selectType(type)"
        >
          <NIcon :size="26" class="type-icon" :color="selectedType.id === type.id ? 'var(--color-primary)' : 'var(--color-text-muted)'">
            <component :is="type.icon" />
          </NIcon>
          <span class="type-label">{{ type.label }}</span>
          <span class="type-desc">{{ type.desc }}</span>
          <div class="type-check" v-if="selectedType.id === type.id">✓</div>
        </button>
      </div>
    </NCard>

    <!-- 输入区域 -->
    <Transition name="slide-fade" mode="out-in">
      <!-- 小程序专用表单 -->
      <NCard v-if="selectedType.id === 'miniprogram'" key="miniprogram" title="写入小程序" class="section-card fade-up">
        <template #header-extra>
          <NIcon :size="18" color="#07c160"><LogoWechat /></NIcon>
        </template>

        <div class="mp-form">
          <!-- 说明提示 -->
          <div class="mp-hint">
            <NIcon :size="16" class="text-muted"><InformationCircleOutline /></NIcon>
            <span>写入后，手机碰一碰 NFC 标签即可打开对应小程序页面</span>
          </div>

          <!-- AppID -->
          <div class="form-field">
            <label class="field-label">
              AppID
              <span class="required">*</span>
            </label>
            <NInput
              v-model:value="mpAppid"
              placeholder="wx1234567890abcdef"
              size="large"
            />
          </div>

          <!-- 页面路径 -->
          <div class="form-field">
            <label class="field-label">
              页面路径
              <span class="required">*</span>
            </label>
            <NInput
              v-model:value="mpPath"
              placeholder="/pages/index/index"
              size="large"
              :status="mpPathError ? 'error' : undefined"
              @blur="validatePath"
            />
            <span v-if="mpPathError" class="field-error">{{ mpPathError }}</span>
          </div>

          <!-- Query 参数 -->
          <div class="form-field">
            <label class="field-label">
              Query 参数
              <NTooltip trigger="hover">
                <template #trigger>
                  <NIcon :size="14" class="label-help"><InformationCircleOutline /></NIcon>
                </template>
                附加到小程序页面的查询参数，最大 512 字符
              </NTooltip>
            </label>
            <NInput
              v-model:value="mpQuery"
              placeholder="id=123&type=detail"
              size="large"
              :status="mpQueryError ? 'error' : undefined"
              @blur="validateQuery"
            />
            <div class="field-meta">
              <span v-if="mpQueryError" class="field-error">{{ mpQueryError }}</span>
              <span class="char-count" :class="{ over: mpQuery.length > 512 }">{{ mpQuery.length }}/512</span>
            </div>
          </div>

          <!-- 环境版本 -->
          <div class="form-field">
            <label class="field-label">环境版本</label>
            <NSelect
              v-model:value="mpEnvVersion"
              :options="mpEnvOptions"
              size="large"
            />
          </div>

          <!-- 预览 -->
          <div v-if="mpScheme" class="scheme-preview">
            <label class="field-label">生成的 URL Scheme</label>
            <div class="scheme-box">
              <code class="scheme-text">{{ mpScheme }}</code>
            </div>
          </div>
        </div>
      </NCard>

      <!-- 通用表单 -->
      <NCard v-else :key="selectedType.id" :title="`写入 ${selectedType.label}`" class="section-card fade-up">
        <template #header-extra>
          <NIcon :size="18" color="var(--color-primary)">
            <component :is="selectedType.icon" />
          </NIcon>
        </template>

        <div class="input-area">
          <div class="input-header">
            <NIcon :size="20" class="text-muted">
              <component :is="selectedType.icon" />
            </NIcon>
            <span class="input-label">{{ selectedType.desc }}</span>
          </div>

          <NInput
            v-model:value="payload"
            :type="formConfig.type"
            :placeholder="formConfig.placeholder"
            :rows="formConfig.rows"
            size="large"
            clearable
          />

          <span class="char-count">{{ payload.length }} 字符</span>
        </div>
      </NCard>
    </Transition>

    <!-- 写入按钮（固定在底部） -->
    <div class="write-action fade-up" style="animation-delay: 200ms">
      <NButton
        type="primary"
        size="large"
        :loading="store.busy"
        :disabled="!canWrite"
        block
        @click="handleWrite"
      >
        <template #icon>
          <NIcon><CreateOutline /></NIcon>
        </template>
        写入标签
      </NButton>
    </div>

    <!-- 写入成功动画 -->
    <Transition name="scale">
      <div v-if="writeSuccess" class="success-overlay">
        <div class="success-icon">✓</div>
        <span class="success-text">写入成功</span>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.write-view {
  max-width: 720px;
  position: relative;
}

.page-header {
  margin-bottom: 24px;
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

.text-muted {
  color: var(--color-text-muted);
}

/* ── 记录类型网格 ── */
.section-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: 16px;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.type-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 16px 10px;
  background: var(--color-bg);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  animation: fade-up-in 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
  overflow: hidden;
}

.type-card:hover {
  border-color: var(--color-border-hover);
  background: var(--color-surface);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.type-card.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.type-icon {
  transition: transform var(--transition-fast);
}

.type-card:hover .type-icon {
  transform: scale(1.1);
}

.type-card.selected .type-icon {
  transform: scale(1.15);
}

.type-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

.type-desc {
  font-size: 11px;
  color: var(--color-text-muted);
  text-align: center;
}

.type-check {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pop-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes pop-in {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

/* ── 小程序表单 ── */
.mp-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.mp-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--color-text-secondary);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 4px;
}

.required {
  color: #e11d48;
  font-size: 14px;
}

.label-help {
  color: var(--color-text-muted);
  cursor: help;
}

.field-error {
  font-size: 12px;
  color: #e11d48;
}

.field-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.char-count {
  font-size: 12px;
  color: var(--color-text-muted);
  align-self: flex-end;
}

.char-count.over {
  color: #e11d48;
  font-weight: 600;
}

/* ── URL Scheme 预览 ── */
.scheme-preview {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.scheme-box {
  padding: 14px 16px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow-x: auto;
}

.scheme-text {
  font-family: "JetBrains Mono", monospace;
  font-size: 12px;
  color: var(--color-primary);
  word-break: break-all;
  white-space: pre-wrap;
  line-height: 1.6;
}

/* ── 通用输入区域 ── */
.input-area {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.input-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

/* ── 写入按钮 ── */
.write-action {
  margin-top: 4px;
}

/* ── 成功覆盖层 ── */
.success-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 60px;
  background: var(--color-surface);
  border: 1px solid var(--color-success);
  border-radius: 20px;
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-lg);
  z-index: 100;
}

.success-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-success), var(--color-primary));
  color: #ffffff;
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: success-bounce 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes success-bounce {
  0% { transform: scale(0) rotate(-20deg); }
  60% { transform: scale(1.2) rotate(5deg); }
  100% { transform: scale(1) rotate(0deg); }
}

.success-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-success);
}

/* ── 动画 ── */
.fade-up {
  animation: fade-up-in 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes fade-up-in {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.slide-fade-enter-active {
  transition: all var(--transition-slow);
}

.slide-fade-leave-active {
  transition: all 200ms ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.scale-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.scale-leave-active {
  transition: all 250ms ease;
}

.scale-enter-from {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.7);
}

.scale-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(1.1);
}
</style>
