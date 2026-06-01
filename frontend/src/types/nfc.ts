export interface NFCReader {
  id: string;
  name: string;
  connected: boolean;
}

export interface NFCTag {
  uid: string;
  records: string[];
}

export interface NFCStatus {
  adapter: string;
  adapterName: string;
  connectedReaderId: string | null;
}

export interface NFCAdapter {
  id: string;
  name: string;
  active: boolean;
}
