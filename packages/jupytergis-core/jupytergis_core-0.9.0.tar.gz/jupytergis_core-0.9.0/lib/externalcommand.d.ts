import { IJGISExternalCommand, IJGISExternalCommandRegistry } from '@jupytergis/schema';
export declare class JupyterGISExternalCommandRegistry implements IJGISExternalCommandRegistry {
    constructor();
    registerCommand(cmd: IJGISExternalCommand): void;
    getCommands(): IJGISExternalCommand[];
    private _registry;
}
