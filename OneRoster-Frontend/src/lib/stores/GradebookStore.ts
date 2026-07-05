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
export const classResults = ref<OneRosterRecord[]>([])
export const categories = ref<OneRosterRecord[]>([])

export const selectedGradebookStudentId = ref('all')
export const gradebookAverage = computed(() => average(classResults.value.map((result) => Number(result.score))))
export const filteredClassResults = computed(() => {
  if (selectedGradebookStudentId.value === 'all') {
    return classResults.value
  }

  return classResults.value.filter(
    (result) => getGuidRef(result.student).sourcedId === selectedGradebookStudentId.value,
  )
})