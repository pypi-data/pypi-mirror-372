export class JupyterGISExternalCommandRegistry {
    constructor() {
        this._registry = new Set();
    }
    registerCommand(cmd) {
        this._registry.add(cmd);
    }
    getCommands() {
        return [...this._registry];
    }
}
