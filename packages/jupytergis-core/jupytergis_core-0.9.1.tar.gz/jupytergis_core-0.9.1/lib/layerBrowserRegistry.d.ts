import { IJGISLayerBrowserRegistry, IRasterLayerGalleryEntry } from '@jupytergis/schema';
/**
 * Manages a registry of raster layer gallery entries for a Jupyter GIS Layer Browser.
 * Implements the {@link IJGISLayerBrowserRegistry} interface, allowing for the addition, removal, and retrieval of raster layer entries.
 *
 * @class JupyterGISLayerBrowserRegistry
 * @implements IJGISLayerBrowserRegistry
 */
export declare class JupyterGISLayerBrowserRegistry implements IJGISLayerBrowserRegistry {
    private _registry;
    constructor();
    /**
     * Retrieves the current state of the registry layers.
     * Returns a copy of the internal registry array to prevent external modifications.
     * @returns The current state of the registry layers.
     */
    getRegistryLayers(): IRasterLayerGalleryEntry[];
    /**
     * Adds a new raster layer gallery entry to the registry.
     * @param data - The raster layer gallery entry to add.
     */
    addRegistryLayer(data: IRasterLayerGalleryEntry): void;
    /**
     * Removes a raster layer gallery entry from the registry by its name.
     * @param name - The name of the raster layer gallery entry to remove.
     */
    removeRegistryLayer(name: string): void;
    /**
     * Clears the entire registry of raster layer gallery entries.
     */
    clearRegistry(): void;
}
