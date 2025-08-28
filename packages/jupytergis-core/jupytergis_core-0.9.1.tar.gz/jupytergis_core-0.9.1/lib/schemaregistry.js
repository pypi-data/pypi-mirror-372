import formSchema from '@jupytergis/schema/lib/_interface/forms.json';
export class JupyterGISFormSchemaRegistry {
    constructor(docManager) {
        this._registry = new Map(Object.entries(formSchema));
        this._docManager = docManager;
    }
    registerSchema(name, schema) {
        if (!this._registry.has(name)) {
            this._registry.set(name, schema);
        }
        else {
            console.error('Worker is already registered!');
        }
    }
    has(name) {
        return this._registry.has(name);
    }
    getSchemas() {
        return this._registry;
    }
    getDocManager() {
        return this._docManager;
    }
}
