import { IDict, IJGISFormSchemaRegistry } from '@jupytergis/schema';
import { IDocumentManager } from '@jupyterlab/docmanager';
export declare class JupyterGISFormSchemaRegistry implements IJGISFormSchemaRegistry {
    private _docManager;
    constructor(docManager: IDocumentManager);
    registerSchema(name: string, schema: IDict): void;
    has(name: string): boolean;
    getSchemas(): Map<string, IDict>;
    getDocManager(): IDocumentManager;
    private _registry;
}
