import { computed, ref } from 'vue'
import { getGuidRef } from '../heplers'

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
import { type MetricCard } from '@/lib/oneroster'

export const courseResources = ref<OneRosterRecord[]>([])

export const resourceMode = ref<ResourceMode>('classes')
export const resources = ref<OneRosterRecord[]>([])
