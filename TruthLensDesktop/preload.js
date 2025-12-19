const { contextBridge } = require('electron');

// We don't need complex IPC for now as we can use fetch/axios directly in renderer 
// if we disable some security or use a proper bridge.
// Since it's a simple client, we'll expose a version or health check if needed.

contextBridge.exposeInMainWorld('api', {
    version: '1.0.0',
    appTitle: 'TruthLens'
});
