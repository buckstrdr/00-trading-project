import http from 'http';
declare class ChartWebSocket {
    private io;
    constructor(server: http.Server);
    broadcast(event: string, data: any): void;
    getConnectedClients(): number;
}
export default ChartWebSocket;
//# sourceMappingURL=chart-websocket.d.ts.map