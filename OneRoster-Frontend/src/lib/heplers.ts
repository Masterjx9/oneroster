
import {
  ALL_SCOPES,
  average,
  collectionFromResponse,
  formatDate,
  guidRefs,
  joinBaseUrl,
  listOf,
  recordSubtitle,
  recordTitle,
  refLabel,
  SAMPLE_IDS,
  type AppView,
  type OneRosterRecord,
  type PersonMode,
  type ResourceMode,
  type TokenPayload,
  VIEW_OPTIONS,
} from '@/lib/oneroster'

export function getGuidRef(value: unknown): { sourcedId: string } {
  if (value && typeof value === 'object' && 'sourcedId' in value) {
    return value as { sourcedId: string }
  }

  return { sourcedId: '' }
}

export function relatedRecord(collection: OneRosterRecord[], refValue: unknown): OneRosterRecord | null {
  const ref = getGuidRef(refValue)
  return collection.find((item) => item.sourcedId === ref.sourcedId) ?? null
}