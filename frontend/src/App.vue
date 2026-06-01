<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { getBridge, unwrap } from "./services/bridge";
import type { NFCReader, NFCStatus, NFCTag } from "./types/nfc";

const bridge = getBridge();

const readers = ref<NFCReader[]>([]);
const status = ref<NFCStatus>({ adapter: "mock", connectedReaderId: null });
const tag = ref<NFCTag | null>(null);
const payload = ref("Hello from NFC Writer");
const busy = ref(false);
const error = ref("");
const notice = ref("");

const selectedReaderId = computed(() => status.value.connectedReaderId ?? readers.value[0]?.id ?? "");
const connectedReader = computed(() =>
  readers.value.find((reader) => reader.id === status.value.connectedReaderId),
);

async function runTask(task: () => Promise<void>, successMessage = "") {
  busy.value = true;
  error.value = "";
  notice.value = "";
  try {
    await task();
    notice.value = successMessage;
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : "Unexpected operation failure.";
  } finally {
    busy.value = false;
  }
}

async function refreshReaders() {
  readers.value = await unwrap(await bridge.list_readers());
  status.value = await unwrap(await bridge.status());
}

async function connect(readerId: string) {
  await runTask(async () => {
    const reader = await unwrap(await bridge.connect(readerId));
    status.value.connectedReaderId = reader.id;
    await refreshReaders();
  }, "Reader connected.");
}

async function disconnect() {
  await runTask(async () => {
    status.value = await unwrap(await bridge.disconnect());
    tag.value = null;
    await refreshReaders();
  }, "Reader disconnected.");
}

async function readTag() {
  await runTask(async () => {
    tag.value = await unwrap(await bridge.read_tag());
  }, "Tag read complete.");
}

async function writeText() {
  await runTask(async () => {
    tag.value = await unwrap(await bridge.write_text(payload.value));
  }, "Text record written.");
}

onMounted(() => {
  void runTask(refreshReaders);
});
</script>

<template>
  <main class="app-shell">
    <section class="hero">
      <div>
        <p class="eyebrow">Desktop NFC Console</p>
        <h1>NFC Writer</h1>
        <p class="lede">Read tags, write text records, and swap hardware adapters behind one pywebview bridge.</p>
      </div>
      <div class="status-cluster" aria-live="polite">
        <span class="status-pill" :data-active="Boolean(connectedReader)">
          {{ connectedReader ? "Connected" : "No reader" }}
        </span>
        <span class="muted">Adapter: {{ status.adapter }}</span>
      </div>
    </section>

    <section class="workspace" aria-label="NFC workspace">
      <div class="panel">
        <div class="panel-heading">
          <div>
            <h2>Readers</h2>
            <p>Select the active NFC reader.</p>
          </div>
          <button type="button" class="ghost-button" :disabled="busy" @click="runTask(refreshReaders)">Refresh</button>
        </div>

        <div v-if="readers.length === 0" class="empty-state">No NFC readers found.</div>
        <div v-else class="reader-list">
          <button
            v-for="reader in readers"
            :key="reader.id"
            type="button"
            class="reader-row"
            :class="{ selected: reader.id === selectedReaderId }"
            :disabled="busy"
            @click="connect(reader.id)"
          >
            <span>{{ reader.name }}</span>
            <small>{{ reader.connected ? "Active" : reader.id }}</small>
          </button>
        </div>

        <button type="button" class="danger-button" :disabled="busy || !connectedReader" @click="disconnect">
          Disconnect
        </button>
      </div>

      <div class="panel">
        <div class="panel-heading">
          <div>
            <h2>Tag</h2>
            <p>Read the presented tag before writing.</p>
          </div>
          <button type="button" class="primary-button" :disabled="busy || !connectedReader" @click="readTag">
            Read
          </button>
        </div>

        <div v-if="tag" class="tag-card">
          <span class="muted">UID</span>
          <strong>{{ tag.uid }}</strong>
          <span class="muted">Records</span>
          <p v-for="(record, index) in tag.records" :key="index">{{ record }}</p>
        </div>
        <div v-else class="empty-state">No tag data loaded.</div>
      </div>

      <div class="panel write-panel">
        <div class="panel-heading">
          <div>
            <h2>Write Text</h2>
            <p>Create a simple text record for the active tag.</p>
          </div>
        </div>
        <textarea v-model="payload" :disabled="busy" rows="6" aria-label="Text payload" />
        <button type="button" class="primary-button" :disabled="busy || !connectedReader" @click="writeText">
          Write
        </button>
      </div>
    </section>

    <p v-if="busy" class="feedback">Working...</p>
    <p v-else-if="error" class="feedback error" role="alert">{{ error }}</p>
    <p v-else-if="notice" class="feedback success">{{ notice }}</p>
  </main>
</template>
