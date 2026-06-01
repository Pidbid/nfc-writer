import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { getBridge, unwrap } from "../services/bridge";
import type { NFCAdapter, NFCReader, NFCStatus, NFCTag } from "../types/nfc";

export interface HistoryEntry {
  id: number;
  time: Date;
  action: "read" | "write" | "connect" | "disconnect";
  detail: string;
  success: boolean;
}

export const useNfcStore = defineStore("nfc", () => {
  const bridge = getBridge();

  // ── 状态 ──
  const readers = ref<NFCReader[]>([]);
  const adapters = ref<NFCAdapter[]>([]);
  const status = ref<NFCStatus>({
    adapter: "pyscard",
    adapterName: "标准 PC/SC",
    connectedReaderId: null,
  });
  const tag = ref<NFCTag | null>(null);
  const busy = ref(false);
  const error = ref("");
  const notice = ref("");
  const history = ref<HistoryEntry[]>([]);
  let historyId = 0;

  // ── 计算属性 ──
  const connectedReader = computed(() =>
    readers.value.find((r) => r.id === status.value.connectedReaderId),
  );

  // ── 内部方法 ──
  function pushHistory(
    action: HistoryEntry["action"],
    detail: string,
    success: boolean,
  ) {
    history.value.unshift({
      id: ++historyId,
      time: new Date(),
      action,
      detail,
      success,
    });
    if (history.value.length > 200) history.value.length = 200;
  }

  async function runTask(task: () => Promise<void>, successMessage = "") {
    busy.value = true;
    error.value = "";
    notice.value = "";
    try {
      await task();
      notice.value = successMessage;
    } catch (caught) {
      error.value =
        caught instanceof Error ? caught.message : "Unexpected operation failure.";
    } finally {
      busy.value = false;
    }
  }

  // ── 适配器操作 ──
  async function loadAdapters() {
    const [statusRes, adaptersRes] = await Promise.all([
      bridge.status(),
      bridge.list_adapters(),
    ]);
    if (statusRes.ok && statusRes.data) status.value = statusRes.data;
    if (adaptersRes.ok && adaptersRes.data) adapters.value = adaptersRes.data;
  }

  async function setAdapter(adapterName: string) {
    if (adapterName === status.value.adapter) return;
    await runTask(async () => {
      status.value = await unwrap(await bridge.set_adapter(adapterName));
      tag.value = null;
      readers.value = await unwrap(await bridge.list_readers());
      adapters.value = adapters.value.map((a) => ({
        ...a,
        active: a.id === adapterName,
      }));
    }, `已切换到 ${status.value.adapterName}`);
  }

  // ── 读写器操作 ──
  async function refreshReaders() {
    readers.value = await unwrap(await bridge.list_readers());
    status.value = await unwrap(await bridge.status());
  }

  async function connect(readerId: string) {
    await runTask(async () => {
      const reader = await unwrap(await bridge.connect(readerId));
      status.value.connectedReaderId = reader.id;
      pushHistory("connect", `Connected to ${reader.name}`, true);
      await refreshReaders();
    }, "Reader connected.");
  }

  async function disconnect() {
    await runTask(async () => {
      const name = connectedReader.value?.name ?? "reader";
      status.value = await unwrap(await bridge.disconnect());
      tag.value = null;
      pushHistory("disconnect", `Disconnected from ${name}`, true);
      await refreshReaders();
    }, "Reader disconnected.");
  }

  // ── 标签操作 ──
  async function readTag() {
    await runTask(async () => {
      tag.value = await unwrap(await bridge.read_tag());
      pushHistory(
        "read",
        `Read tag ${tag.value.uid} — ${tag.value.records.length} record(s)`,
        true,
      );
    }, "Tag read complete.");
  }

  async function writeText(text: string) {
    await runTask(async () => {
      tag.value = await unwrap(await bridge.write_text(text));
      pushHistory("write", `Wrote text record to ${tag.value.uid}`, true);
    }, "Text record written.");
  }

  async function writeUri(uri: string) {
    await runTask(async () => {
      tag.value = await unwrap(await bridge.write_uri(uri));
      pushHistory("write", `Wrote URI record to ${tag.value.uid}`, true);
    }, "URI record written.");
  }

  // ── 初始化 ──
  async function initialize() {
    await runTask(loadAdapters);
  }

  return {
    // 状态
    readers,
    adapters,
    status,
    tag,
    busy,
    error,
    notice,
    history,
    connectedReader,
    // 操作
    initialize,
    setAdapter,
    refreshReaders,
    connect,
    disconnect,
    readTag,
    writeText,
    writeUri,
    runTask,
  };
});
