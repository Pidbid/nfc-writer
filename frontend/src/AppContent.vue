<script setup lang="ts">
import { useMessage } from "naive-ui";
import { watch } from "vue";

import { useNfcStore } from "./stores/nfc";
import DashboardView from "./views/DashboardView.vue";
import HistoryView from "./views/HistoryView.vue";
import ReadView from "./views/ReadView.vue";
import WriteView from "./views/WriteView.vue";

defineProps<{ activePage: string }>();

const message = useMessage();
const store = useNfcStore();

watch(() => store.notice, (v) => { if (v) message.success(v); });
watch(() => store.error, (v) => { if (v) message.error(v); });
</script>

<template>
  <main class="main-content">
    <Transition name="page" mode="out-in">
      <DashboardView v-if="activePage === 'dashboard'" key="dashboard" />
      <ReadView v-else-if="activePage === 'read'" key="read" />
      <WriteView v-else-if="activePage === 'write'" key="write" />
      <HistoryView v-else-if="activePage === 'history'" key="history" />
    </Transition>
  </main>
</template>

<style scoped>
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 32px 40px;
  background: var(--color-bg);
}

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
</style>
