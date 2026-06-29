export interface NamedRecord {
  id: string;
  name: string;
}

export function buildNameLookup(records: NamedRecord[]): Map<string, string> {
  return new Map(records.map((record) => [record.id, record.name]));
}

export function lookupName(
  map: Map<string, string>,
  id: string | null | undefined,
  fallback = "—",
): string {
  const key = id?.trim();
  if (!key) return fallback;
  return map.get(key) ?? fallback;
}
