import { computed, onMounted, ref } from "vue";

import { getBridge, unwrap } from "../services/bridge";
import type { NFCReader, NFCStatus, NFCTag } from "../types/nfc";

export interface HistoryEntry {
  id: number;
  time: Date;
  action: "read" | "write" | "connect" | "disconnect";
  detail: string;
  success: boolean;
}

let bridge: ReturnType<typeof getBridge> | null = null;
let initialized = false;

const readers = ref<NFCReader[]>([]);
const status = ref<NFCStatus>({ adapter: "mock", connectedReaderId: null });
const tag = ref<NFCTag | null>(null);
const busy = ref(false);
const error = ref("");
const notice = ref("");
const history = ref<HistoryEntry[]>([]);
let historyId = 0;

function ensureBridge() {
  if (!bridge) bridge = getBridge();
  return bridge;
}

const selectedReaderId = computed(
  () => status.value.connectedReaderId ?? readers.value[0]?.id ?? "",
);

const connectedReader = computed(() =>
  readers.value.find((r) => r.id === status.value.connectedReaderId),
);

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

async function refreshReaders() {
  const b = ensureBridge();
  readers.value = await unwrap(await b.list_readers());
  status.value = await unwrap(await b.status());
}

async function connect(readerId: string) {
  const b = ensureBridge();
  await runTask(async () => {
    const reader = await unwrap(await b.connect(readerId));
    status.value.connectedReaderId = reader.id;
    pushHistory("connect", `Connected to ${reader.name}`, true);
    await refreshReaders();
  }, "Reader connected.");
}

async function disconnect() {
  const b = ensureBridge();
  await runTask(async () => {
    const name = connectedReader.value?.name ?? "reader";
    status.value = await unwrap(await b.disconnect());
    tag.value = null;
    pushHistory("disconnect", `Disconnected from ${name}`, true);
    await refreshReaders();
  }, "Reader disconnected.");
}

async function readTag() {
  const b = ensureBridge();
  await runTask(async () => {
    tag.value = await unwrap(await b.read_tag());
    pushHistory(
      "read",
      `Read tag ${tag.value.uid} — ${tag.value.records.length} record(s)`,
      true,
    );
  }, "Tag read complete.");
}

async function writeText(text: string) {
  const b = ensureBridge();
  await runTask(async () => {
    tag.value = await unwrap(await b.write_text(text));
    pushHistory("write", `Wrote text record to ${tag.value.uid}`, true);
  }, "Text record written.");
}

export function useNfc() {
  onMounted(() => {
    if (!initialized) {
      initialized = true;
      void runTask(refreshReaders);
    }
  });

  return {
    readers,
    status,
    tag,
    busy,
    error,
    notice,
    history,
    selectedReaderId,
    connectedReader,
    refreshReaders,
    connect,
    disconnect,
    readTag,
    writeText,
    runTask,
  };
}
