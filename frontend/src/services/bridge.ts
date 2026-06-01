import type { NFCReader, NFCStatus, NFCTag } from "../types/nfc";

export interface ApiResponse<T> {
  ok: boolean;
  data?: T;
  error?: string;
  errorType?: string;
}

export interface NFCBridgeApi {
  ping: () => Promise<ApiResponse<{ service: string }>>;
  status: () => Promise<ApiResponse<NFCStatus>>;
  list_readers: () => Promise<ApiResponse<NFCReader[]>>;
  connect: (readerId: string) => Promise<ApiResponse<NFCReader>>;
  disconnect: () => Promise<ApiResponse<NFCStatus>>;
  read_tag: () => Promise<ApiResponse<NFCTag>>;
  write_text: (text: string) => Promise<ApiResponse<NFCTag>>;
}

const fallbackApi: NFCBridgeApi = {
  async ping() {
    return { ok: true, data: { service: "browser-preview" } };
  },
  async status() {
    return { ok: true, data: { adapter: "mock", connectedReaderId: null } };
  },
  async list_readers() {
    return {
      ok: true,
      data: [{ id: "preview-reader", name: "Preview NFC Reader", connected: false }],
    };
  },
  async connect(readerId: string) {
    return { ok: true, data: { id: readerId, name: "Preview NFC Reader", connected: true } };
  },
  async disconnect() {
    return { ok: true, data: { adapter: "mock", connectedReaderId: null } };
  },
  async read_tag() {
    return { ok: true, data: { uid: "PREVIEW:TAG", records: ["Preview payload"] } };
  },
  async write_text(text: string) {
    return { ok: true, data: { uid: "PREVIEW:TAG", records: [text] } };
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
