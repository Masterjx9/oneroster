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
export const schools = ref<OneRosterRecord[]>([])
export const orgs = ref<OneRosterRecord[]>([])
export const selectedSchoolId = ref('')
export const schoolBundleLoading = ref(false)
export const schoolDetailLoading = ref(false)
export const schoolOrgDetailLoading = ref(false)
export const schoolTerms = ref<OneRosterRecord[]>([])
export const schoolEnrollments = ref<OneRosterRecord[]>([])
export const selectedSchoolClassId = ref('')
export const schoolClassBundleLoading = ref(false)
export const schoolClassStudents = ref<OneRosterRecord[]>([])
export const schoolClassTeachers = ref<OneRosterRecord[]>([])
export const schoolClassEnrollments = ref<OneRosterRecord[]>([])
export const selectedSchoolDetail = ref<OneRosterRecord | null>(null)
export const selectedSchoolOrgDetail = ref<OneRosterRecord | null>(null)

export const schoolSearch = ref('')
export const filteredSchools = computed(() => {
  const needle = schoolSearch.value.trim().toLowerCase()
  if (!needle) {
    return schools.value
  }

  return schools.value.filter((school) =>
    [recordTitle(school), recordSubtitle(school), school.sourcedId]
      .join(' ')
      .toLowerCase()
      .includes(needle),
  )
})

export const schoolCourses = ref<OneRosterRecord[]>([])
export const schoolClasses = ref<OneRosterRecord[]>([])
export const schoolStudents = ref<OneRosterRecord[]>([])
export const schoolTeachers = ref<OneRosterRecord[]>([])

export const selectedSchool = computed(
  () => selectedSchoolDetail.value
    ?? selectedSchoolOrgDetail.value
    ?? schools.value.find((school) => school.sourcedId === selectedSchoolId.value)
    ?? null,
)
export const schoolOverviewMetrics = computed<MetricCard[]>(() => [
  { label: 'Courses', value: schoolCourses.value.length, description: 'Course catalog for this school.' },
  { label: 'Classes', value: schoolClasses.value.length, description: 'Classes linked to this school.' },
  { label: 'Students', value: schoolStudents.value.length, description: 'Students attending this school.' },
  { label: 'Teachers', value: schoolTeachers.value.length, description: 'Teachers teaching at this school.' },
])
