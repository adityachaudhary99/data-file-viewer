const TRUST_WARNING_EXTENSIONS = new Set(['.pkl', '.pickle', '.joblib', '.jl']);

export function requiresTrustWarning(ext: string): boolean {
  return TRUST_WARNING_EXTENSIONS.has(ext.toLowerCase());
}
