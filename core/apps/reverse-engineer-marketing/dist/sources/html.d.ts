import type { Discovered } from "../context.js";
export interface PageFacts {
    title: string;
    description: string;
    siteName?: string;
    h1: string[];
    h2: string[];
    ctas: string[];
    links: string[];
    scripts: string[];
    jsonLdTypes: string[];
    sameAs: string[];
    rating?: {
        value: number;
        count: number;
    };
    lang?: string;
    wordCount: number;
    /** Brand image candidates: apple-touch-icon, icons, JSON-LD logo, og:image. */
    logos: LogoCandidate[];
    /** People from JSON-LD `founder` / Person with a founder job title. */
    jsonLdFounders: {
        name: string;
        role?: string;
        url?: string;
    }[];
}
export interface LogoCandidate {
    url: string;
    source: "apple-touch-icon" | "icon" | "jsonld" | "og-image" | "linkedin" | "appstore" | "wikidata" | "instagram" | "favicon";
    size?: number;
}
export declare function pageFacts(html: string, baseUrl: string): PageFacts;
/** Animated headlines often render the same phrase 2–4 times in the DOM. */
export declare function collapseRepeats(t: string): string;
/** First matching handle per platform; site footer links usually win over share buttons. */
export declare function extractSocials(links: string[]): Discovered["socials"];
export declare function extractPeople(links: string[]): string[];
export declare function extractAppIds(links: string[]): {
    apple: string[];
    play: string[];
};
/** utm_* tags on outbound and internal links reveal campaign naming and partner deals. */
export declare function extractUtms(links: string[]): {
    url: string;
    source?: string;
    medium?: string;
    campaign?: string;
}[];
/** Same-site key pages, one per kind. */
export declare function pickKeyPages(home: string, links: string[]): Record<string, string>;
export interface PricingSignals {
    prices: string[];
    freePlan: boolean;
    freeTrial: boolean;
    trialDays?: number;
    moneyBack: boolean;
    contactSales: boolean;
    perSeat: boolean;
    annualDiscount: boolean;
    lifetimeDeal: boolean;
    usageBased: boolean;
}
export declare function pricingSignals(text: string): PricingSignals;
export declare function visibleText(html: string): string;
/** "Zach Yadegari" yes; "Our Team", "Read More", "Cal AI" no. */
export declare function looksLikeName(s: string, brand?: string): boolean;
/** Founder names in free text ("founded by A and B", "A, Co-founder & CEO"). */
export declare function extractFounderNames(text: string, brand?: string): {
    name: string;
    role?: string;
}[];
