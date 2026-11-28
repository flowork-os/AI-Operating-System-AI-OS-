import { type Channel, type EvidenceStore } from "../evidence.js";
export type Status = "active" | "likely" | "dormant" | "none" | "unknown";
export interface ChannelScore {
    channel: Channel;
    status: Status;
    /** 0–3: how much this channel looks like a growth engine for them. */
    strength: 0 | 1 | 2 | 3;
    signal: string;
    evidence: string[];
}
export declare function scorecard(store: EvidenceStore): ChannelScore[];
/** The 1–3 channels doing the heavy lifting, strongest first. */
export declare function engines(card: ChannelScore[]): ChannelScore[];
