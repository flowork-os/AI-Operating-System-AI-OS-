interface Step {
    client: string;
    description: string;
    run: () => void;
    skip?: string;
}
export declare function plan(clients: string[]): Step[];
export declare function setup(opts: {
    clients: string[];
    yes: boolean;
    dryRun: boolean;
    json: boolean;
}): Promise<number>;
export {};
