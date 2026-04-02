export const APP_NAME = "MediaCreator";

export type BootstrapSurface = {
  application: typeof APP_NAME;
  status: "bootstrap-only" | "ready";
};
