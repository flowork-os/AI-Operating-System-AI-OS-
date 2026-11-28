export interface UserConfig {
    scrapecreatorsKey?: string;
}
export declare function readConfig(): UserConfig;
export declare function writeConfig(patch: UserConfig): UserConfig;
/** Env vars win over the config file unless `override` (set from the UI just now). */
export declare function applyConfig(cfg?: UserConfig, override?: boolean): void;
