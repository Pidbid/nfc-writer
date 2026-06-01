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
  connectedReaderId: string | null;
}
