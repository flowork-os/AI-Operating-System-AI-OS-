export type TagCategory = "ads_pixel" | "analytics" | "tag_manager" | "attribution" | "affiliate" | "email" | "chat" | "experimentation" | "visitor_id" | "sales" | "reviews" | "payments" | "site_builder";
export interface DetectedTag {
    id: string;
    name: string;
    category: TagCategory;
    implies?: string;
    ids: string[];
    /** Where we saw it: "page" or a GTM container id. */
    foundIn: string[];
}
export declare function detectTags(text: string, foundIn?: string): DetectedTag[];
export declare function mergeTags(...lists: DetectedTag[][]): DetectedTag[];
