import { computed, ref } from 'vue'

import {
  recordSubtitle,
  recordTitle,
  type OneRosterRecord,
} from '@/lib/oneroster'

export const academicSessions = ref<OneRosterRecord[]>([])
export const academicSessionSearch = ref('')
export const academicSessionDetailLoading = ref(false)
export const selectedAcademicSessionId = ref('')
export const selectedAcademicSessionDetail = ref<OneRosterRecord | null>(null)
export const terms = ref<OneRosterRecord[]>([])
export const gradingPeriods = ref<OneRosterRecord[]>([])
export const selectedTermId = ref('')
export const selectedGradingPeriodId = ref('')
export const termDetailLoading = ref(false)
export const gradingPeriodDetailLoading = ref(false)
export const selectedTermDetail = ref<OneRosterRecord | null>(null)
export const selectedGradingPeriodDetail = ref<OneRosterRecord | null>(null)
export const termClasses = ref<OneRosterRecord[]>([])
export const termGradingPeriods = ref<OneRosterRecord[]>([])

export const filteredAcademicSessions = computed(() => {
  const needle = academicSessionSearch.value.trim().toLowerCase()
  if (!needle) {
    return academicSessions.value
  }

  return academicSessions.value.filter((session) =>
    [recordTitle(session), recordSubtitle(session), session.sourcedId]
      .join(' ')
      .toLowerCase()
      .includes(needle),
  )
})

export const selectedAcademicSession = computed(
  () => selectedAcademicSessionDetail.value
    ?? academicSessions.value.find((session) => session.sourcedId === selectedAcademicSessionId.value)
    ?? null,
)

export const selectedTerm = computed(
  () => selectedTermDetail.value
    ?? terms.value.find((term) => term.sourcedId === selectedTermId.value)
    ?? null,
)

export const selectedGradingPeriod = computed(
  () => selectedGradingPeriodDetail.value
    ?? gradingPeriods.value.find((period) => period.sourcedId === selectedGradingPeriodId.value)
    ?? null,
)
