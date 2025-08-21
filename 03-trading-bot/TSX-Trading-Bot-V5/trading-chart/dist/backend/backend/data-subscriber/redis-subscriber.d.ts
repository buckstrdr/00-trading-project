interface RedisConfig {
    host?: string;
    port?: number;
    password?: string;
    db?: number;
    retryStrategy?: (times: number) => number | void;
}
declare class RedisSubscriber {
    private redis;
    private channels;
    private isConnected;
    constructor(config?: RedisConfig);
    private messageHandlers;
    subscribe(channel: string, callback: (message: string) => void): Promise<void>;
    unsubscribe(channel: string): Promise<void>;
    isHealthy(): boolean;
    close(): Promise<void>;
}
export default RedisSubscriber;
//# sourceMappingURL=redis-subscriber.d.ts.map