import { type Ctx } from "../context.js";
export declare function adLibraryLinks(brand: string, domain?: string): {
    meta: string;
    google: string;
    linkedin: string;
    tiktok: string;
    tiktokTopAds: string;
    reddit: string;
    x: string;
};
export declare function collectPaid(ctx: Ctx): Promise<void>;
/** First image / video in a Meta ad snapshot (incl. carousel cards). */
export declare function metaMedia(snap: any): {
    thumb?: string;
    video?: string;
};
/**
 * App Store links in ads leak the campaign setup: `ppid` = a custom product page
 * (a tailored App Store page per audience/angle), `ct`/`pt` = App Analytics
 * campaign / provider tokens, plus any attribution parameters.
 */
export declare function appStoreLinkStats(urls: unknown[]): {
    linksToAppStore: number;
    customProductPages: Record<string, number>;
    campaignTokens: Record<string, number>;
    providerTokens: Record<string, number>;
    otherParams: Record<string, number>;
};
export declare function tally(xs: unknown[]): Record<string, number>;
