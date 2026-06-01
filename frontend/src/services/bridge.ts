import type { NFCAdapter, NFCReader, NFCStatus, NFCTag } from "../types/nfc";

export interface ApiResponse<T> {
  ok: boolean;
  data?: T;
  error?: string;
  errorType?: string;
}

export interface NFCBridgeApi {
  ping: () => Promise<ApiResponse<{ service: string }>>;
  status: () => Promise<ApiResponse<NFCStatus>>;
  list_adapters: () => Promise<ApiResponse<NFCAdapter[]>>;
  set_adapter: (adapterName: string) => Promise<ApiResponse<NFCStatus>>;
  list_readers: () => Promise<ApiResponse<NFCReader[]>>;
  connect: (readerId: string) => Promise<ApiResponse<NFCReader>>;
  disconnect: () => Promise<ApiResponse<NFCStatus>>;
  read_tag: () => Promise<ApiResponse<NFCTag>>;
  write_text: (text: string) => Promise<ApiResponse<NFCTag>>;
  write_uri: (uri: string) => Promise<ApiResponse<NFCTag>>;
}

const ADAPTERS: NFCAdapter[] = [
  { id: "pyscard", name: "标准 PC/SC", active: true },
  { id: "xinheng", name: "莘航 RFID", active: false },
];

// 浏览器预览模式下的本地状态
let currentAdapterId = "pyscard";

function getAdapterName(id: string): string {
  return ADAPTERS.find((a) => a.id === id)?.name ?? id;
}

const fallbackApi: NFCBridgeApi = {
  async ping() {
    return { ok: true, data: { service: "browser-preview" } };
  },
  async status() {
    return {
      ok: true,
      data: {
        adapter: currentAdapterId,
        adapterName: getAdapterName(currentAdapterId),
        connectedReaderId: null,
      },
    };
  },
  async list_adapters() {
    return {
      ok: true,
      data: ADAPTERS.map((a) => ({ ...a, active: a.id === currentAdapterId })),
    };
  },
  async set_adapter(adapterName: string) {
    const found = ADAPTERS.find((a) => a.id === adapterName);
    if (!found) {
      return { ok: false, error: `未知适配器: ${adapterName}` };
    }
    currentAdapterId = adapterName;
    return {
      ok: true,
      data: {
        adapter: currentAdapterId,
        adapterName: getAdapterName(currentAdapterId),
        connectedReaderId: null,
      },
    };
  },
  async list_readers() {
    return { ok: true, data: [] };
  },
  async connect(readerId: string) {
    return { ok: true, data: { id: readerId, name: readerId, connected: true } };
  },
  async disconnect() {
    return {
      ok: true,
      data: {
        adapter: currentAdapterId,
        adapterName: getAdapterName(currentAdapterId),
        connectedReaderId: null,
      },
    };
  },
  async read_tag() {
    return { ok: true, data: { uid: "", records: [] } };
  },
  async write_text(text: string) {
    return { ok: true, data: { uid: "", records: [text] } };
  },
  async write_uri(uri: string) {
    return { ok: true, data: { uid: "", records: [uri] } };
  },
};

export function getBridge(): NFCBridgeApi {
  return window.pywebview?.api ?? fallbackApi;
}

export function unwrap<T>(response: ApiResponse<T>): T {
  if (!response.ok || response.data === undefined) {
    throw new Error(response.error ?? "Bridge call failed.");
  }
  return response.data;
}
