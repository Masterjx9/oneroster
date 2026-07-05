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


export const classSearch = ref('')
export const selectedClassId = ref('')
export const classes = ref<OneRosterRecord[]>([])
export const classStudents = ref<OneRosterRecord[]>([])
export const classTeachers = ref<OneRosterRecord[]>([])
export const classResources = ref<OneRosterRecord[]>([])
export const enrollments = ref<OneRosterRecord[]>([])
export const classEnrollments = ref<OneRosterRecord[]>([])
export const selectedEnrollmentId = ref('')
export const selectedEnrollmentDetail = ref<OneRosterRecord | null>(null)

export const filteredClasses = computed(() => {
  const needle = classSearch.value.trim().toLowerCase()
  if (!needle) {
    return classes.value
  }

  return classes.value.filter((item) =>
    [recordTitle(item), recordSubtitle(item), item.sourcedId]
      .join(' ')
      .toLowerCase()
      .includes(needle),
  )
})

export const selectedClassDetail = ref<OneRosterRecord | null>(null)
export const classDetailLoading = ref(false)
export const enrollmentDetailLoading = ref(false)
export const selectedClass = computed(
  () => selectedClassDetail.value
    ?? classes.value.find((item) => item.sourcedId === selectedClassId.value)
    ?? null,
)
export const classLineItems = ref<OneRosterRecord[]>([])
export const courses = ref<OneRosterRecord[]>([])
export const courseClasses = ref<OneRosterRecord[]>([])
export const selectedCourseId = ref('')
export const selectedCourseDetail = ref<OneRosterRecord | null>(null)
export const classBundleLoading = ref(false)
export const courseResourceLoading = ref(false)
export const courseDetailLoading = ref(false)

export const classOverviewMetrics = computed<MetricCard[]>(() => [
  { label: 'Students', value: classStudents.value.length, description: 'Students in the selected class.' },
  { label: 'Teachers', value: classTeachers.value.length, description: 'Teachers assigned to the class.' },
  { label: 'Resources', value: classResources.value.length, description: 'Materials linked to the class.' },
  { label: 'Line Items', value: classLineItems.value.length, description: 'Gradebook columns for the class.' },
])
export const selectedCourse = computed(
  () => selectedCourseDetail.value
    ?? courses.value.find((course) => course.sourcedId === selectedCourseId.value)
    ?? null,
)
