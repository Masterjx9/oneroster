import { computed, ref } from 'vue'
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

export const personMode = ref<PersonMode>('students')
export const users = ref<OneRosterRecord[]>([])
export const students = ref<OneRosterRecord[]>([])
export const teachers = ref<OneRosterRecord[]>([])
export const demographics = ref<OneRosterRecord[]>([])
export const personClasses = ref<OneRosterRecord[]>([])
export const userClasses = ref<OneRosterRecord[]>([])
export const selectedStudentId = ref('')
export const selectedTeacherId = ref('')
export const personBundleLoading = ref(false)
export const personDetailLoading = ref(false)
export const personDemographicLoading = ref(false)
export const selectedPersonDetail = ref<OneRosterRecord | null>(null)
export const selectedPersonDemographic = ref<OneRosterRecord | null>(null)
export const selectedUserDetail = ref<OneRosterRecord | null>(null)
export const selectedPerson = computed(
  () => selectedPersonDetail.value
    ?? (personMode.value === 'students' ? selectedStudent.value : selectedTeacher.value),
)
const selectedStudent = computed(() => students.value.find((student) => student.sourcedId === selectedStudentId.value) ?? null)
const selectedTeacher = computed(() => teachers.value.find((teacher) => teacher.sourcedId === selectedTeacherId.value) ?? null)
