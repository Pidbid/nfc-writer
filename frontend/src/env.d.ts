/// <reference types="vite/client" />

import type { NFCBridgeApi } from "./services/bridge";

declare global {
  interface Window {
    pywebview?: {
      api: NFCBridgeApi;
    };
  }
}
