<script setup lang="ts">
import People from './components/People.vue'
import Gradebook from './components/Gradebook.vue'
import Schools from './components/Schools.vue'
import Classes from './components/Classes.vue'
import Resources from './components/Resources.vue'
import OverviewHub from './components/Overview-Hub.vue'
import OverviewSnapshots from './components/Overview-Snapshots.vue'
import { computed, onMounted, ref, watch } from 'vue'
import { useStorage } from '@vueuse/core'
import {
  Shield,
  Sparkles
} from '@lucide/vue'

import AppHeader from '@/components/AppHeader.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Card,
  CardContent,
} from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  ALL_SCOPES,
  collectionFromResponse,
  joinBaseUrl,
  normalizeBaseUrl,
  SAMPLE_IDS,
  type AppView,
  type OneRosterRecord,
  type PersonMode,
  type TokenPayload,
  VIEW_OPTIONS,
} from '@/lib/oneroster'
import {
  academicSessions,
  academicSessionDetailLoading,
  gradingPeriods,
  gradingPeriodDetailLoading,
  selectedAcademicSessionDetail,
  selectedAcademicSessionId,
  selectedGradingPeriodDetail,
  selectedGradingPeriodId,
  selectedTermDetail,
  selectedTermId,
  termClasses,
  termDetailLoading,
  termGradingPeriods,
  terms,
} from '@/lib/stores/AcademicSessionsStore'

import {
  demographics,
  personBundleLoading,
  personClasses,
  personDemographicLoading,
  personDetailLoading,
  personMode,
  selectedPersonDemographic,
  selectedPersonDetail,
  selectedStudentId,
  selectedTeacherId,
  students,
  teachers,
  selectedUserDetail,
  userClasses,
  users,
} from './lib/stores/PeopleStore'
import {
  selectedGradebookStudentId,
  categories,
  classResults
} from '@/lib/stores/GradebookStore';
import {
  resources,
  courseResources
} from '@/lib/stores/ResourcesStore.ts'
import {
  selectedClassId,
  selectedClassDetail,
  selectedEnrollmentDetail,
  selectedEnrollmentId,
  classLineItems,
  classDetailLoading,
  classes,
  classEnrollments,
  courseClasses,
  enrollmentDetailLoading,
  enrollments,
  classStudents,
  courses,
  selectedCourseDetail,
  classTeachers,
  classResources,
  selectedCourseId,
  classBundleLoading,
  courseResourceLoading,
  courseDetailLoading
} from '@/lib/stores/ClassesStore'

import {
  schoolClasses,
  orgs,
  schools,
  schoolClassEnrollments,
  schoolClassStudents,
  schoolClassTeachers,
  schoolEnrollments,
  schoolOrgDetailLoading,
  schoolTeachers,
  selectedSchoolClassId,
  selectedSchoolDetail,
  selectedSchoolOrgDetail,
  selectedSchoolId,
  schoolStudents,
  schoolCourses,
  schoolBundleLoading,
  schoolTerms,
  schoolDetailLoading,
  schoolClassBundleLoading
} from '@/lib/stores/SchoolsStore'
import { getGuidRef } from '@/lib/heplers'


const baseUrl = useStorage('oneroster-base-url', '/ims/oneroster/v1p1')
const clientId = useStorage('oneroster-client-id', 'oneroster-client')
const clientSecret = useStorage('oneroster-client-secret', 'oneroster-secret')
const accessToken = useStorage('oneroster-access-token', '')
const tokenExpiresAt = useStorage<number | null>('oneroster-token-expires-at', null)

const activeView = ref<AppView>('dashboard')
const tokenLoading = ref(false)
const bootstrapLoading = ref(false)
const connectionSettingsOpen = ref(false)
const connectError = ref('')
const dataError = ref('')

const normalizedTokenExpiresAt = computed(() => {
  if (tokenExpiresAt.value == null) {
    return null
  }

  const value = Number(tokenExpiresAt.value)
  return Number.isFinite(value) ? value : null
})

const tokenReady = computed(() => Boolean(accessToken.value))
const tokenExpired = computed(() => normalizedTokenExpiresAt.value !== null && Date.now() >= normalizedTokenExpiresAt.value)
const tokenStateLabel = computed(() => {
  if (!tokenReady.value) {
    return 'Not connected'
  }
  if (tokenExpired.value) {
    return 'Expired'
  }
  return 'Connected'
})

const tokenExpiryLabel = computed(() => {
  if (!normalizedTokenExpiresAt.value) {
    return 'No expiration captured'
  }
  return new Date(normalizedTokenExpiresAt.value).toLocaleString()
})

const connected = computed(() => tokenReady.value && !tokenExpired.value)
const primaryViews = computed(() => VIEW_OPTIONS)


function chooseDefaultId(items: OneRosterRecord[], preferredId: string): string {
  return items.find((item) => item.sourcedId === preferredId)?.sourcedId ?? items[0]?.sourcedId ?? ''
}

async function parsePayload(response: Response): Promise<unknown> {
  const raw = await response.text()
  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw)
  } catch {
    return raw
  }
}

function payloadErrorMessage(payload: unknown, fallback: string): string {
  if (payload && typeof payload === 'object') {
    const record = payload as Record<string, unknown>
    if (typeof record.error_description === 'string') {
      return record.error_description
    }
    if (typeof record.error === 'string') {
      return record.error
    }
  }

  if (typeof payload === 'string' && payload.trim()) {
    return payload
  }

  return fallback
}

async function requestJson(path: string): Promise<unknown> {
  const headers = new Headers({
    Accept: 'application/json',
  })

  if (accessToken.value) {
    headers.set('Authorization', `Bearer ${accessToken.value}`)
  }

  const response = await fetch(joinBaseUrl(baseUrl.value, path), {
    method: 'GET',
    headers,
  })

  const payload = await parsePayload(response)
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      accessToken.value = ''
      tokenExpiresAt.value = null
      throw new Error('Authorization expired or rejected. Connect again.')
    }
    throw new Error(payloadErrorMessage(payload, `Request failed for ${path}`))
  }

  return payload
}

async function fetchCollection<T extends OneRosterRecord>(path: string, key: string): Promise<T[]> {
  const payload = await requestJson(path)
  return collectionFromResponse<T>(payload, key)
}

async function fetchRecord<T extends OneRosterRecord>(path: string, key: string): Promise<T | null> {
  const payload = await requestJson(path)
  if (!payload || typeof payload !== 'object') {
    return null
  }

  const record = (payload as Record<string, unknown>)[key]
  return record && typeof record === 'object' ? (record as T) : null
}

async function issueToken() {
  tokenLoading.value = true
  connectError.value = ''

  try {
    const basic = btoa(`${clientId.value}:${clientSecret.value}`)
    const response = await fetch(joinBaseUrl(baseUrl.value, '/token'), {
      method: 'POST',
      headers: {
        Authorization: `Basic ${basic}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        scope: ALL_SCOPES.join(' '),
      }).toString(),
    })

    const payload = (await parsePayload(response)) as TokenPayload | string | null
    if (!response.ok || !payload || typeof payload === 'string' || !payload.access_token) {
      throw new Error(payloadErrorMessage(payload, 'Unable to issue a bearer token'))
    }

    accessToken.value = payload.access_token
    tokenExpiresAt.value = payload.expires_in ? Date.now() + payload.expires_in * 1000 : null
  } catch (error) {
    accessToken.value = ''
    tokenExpiresAt.value = null
    connectError.value = error instanceof Error ? error.message : 'Unknown token error'
  } finally {
    tokenLoading.value = false
  }
}

async function bootstrapData() {
  if (!connected.value) {
    return
  }

  bootstrapLoading.value = true
  dataError.value = ''

  const specs = [
    { key: 'academicSessions', path: '/academicSessions', assign: (items: OneRosterRecord[]) => { academicSessions.value = items } },
    { key: 'terms', path: '/terms', assign: (items: OneRosterRecord[]) => { terms.value = items } },
    { key: 'gradingPeriods', path: '/gradingPeriods', assign: (items: OneRosterRecord[]) => { gradingPeriods.value = items } },
    { key: 'schools', path: '/schools', assign: (items: OneRosterRecord[]) => { schools.value = items } },
    { key: 'orgs', path: '/orgs', assign: (items: OneRosterRecord[]) => { orgs.value = items } },
    { key: 'classes', path: '/classes', assign: (items: OneRosterRecord[]) => { classes.value = items } },
    { key: 'enrollments', path: '/enrollments', assign: (items: OneRosterRecord[]) => { enrollments.value = items } },
    { key: 'users', path: '/users', assign: (items: OneRosterRecord[]) => { users.value = items } },
    { key: 'students', path: '/students', assign: (items: OneRosterRecord[]) => { students.value = items } },
    { key: 'teachers', path: '/teachers', assign: (items: OneRosterRecord[]) => { teachers.value = items } },
    { key: 'demographics', path: '/demographics', assign: (items: OneRosterRecord[]) => { demographics.value = items } },
    { key: 'courses', path: '/courses', assign: (items: OneRosterRecord[]) => { courses.value = items } },
    { key: 'resources', path: '/resources', assign: (items: OneRosterRecord[]) => { resources.value = items } },
    { key: 'categories', path: '/categories', assign: (items: OneRosterRecord[]) => { categories.value = items } },
  ] as const

  const results = await Promise.allSettled(
    specs.map((spec) => fetchCollection(spec.path, spec.key)),
  )

  const failures: string[] = []
  results.forEach((result, index) => {
    const spec = specs[index]
    if (!spec) {
      return
    }

    if (result.status === 'fulfilled') {
      spec.assign(result.value)
    } else {
      failures.push(result.reason instanceof Error ? result.reason.message : String(result.reason))
    }
  })

  selectedAcademicSessionId.value = chooseDefaultId(academicSessions.value, 'ACAD_SESS_1')
  selectedTermId.value = chooseDefaultId(terms.value, 'ACAD_SESS_2')
  selectedGradingPeriodId.value = chooseDefaultId(gradingPeriods.value, 'ACAD_SESS_3')
  selectedSchoolId.value = chooseDefaultId(schools.value, SAMPLE_IDS.school)
  selectedClassId.value = chooseDefaultId(classes.value, SAMPLE_IDS.class)
  selectedStudentId.value = chooseDefaultId(students.value, SAMPLE_IDS.student)
  selectedTeacherId.value = chooseDefaultId(teachers.value, SAMPLE_IDS.teacher)
  selectedCourseId.value = chooseDefaultId(courses.value, SAMPLE_IDS.course)

  if (selectedAcademicSessionId.value) {
    await loadAcademicSessionDetail(selectedAcademicSessionId.value)
  }

  if (failures.length) {
    dataError.value = failures.join(' | ')
  }

  bootstrapLoading.value = false
}

async function connectWorkspace() {
  await issueToken()

  if (connected.value) {
    await bootstrapData()
  }
}

async function refreshWorkspace() {
  await bootstrapData()
}

async function loadAcademicSessionDetail(sessionId: string) {
  if (!connected.value || !sessionId) {
    selectedAcademicSessionDetail.value = null
    return
  }

  academicSessionDetailLoading.value = true
  dataError.value = ''

  try {
    selectedAcademicSessionDetail.value = await fetchRecord<OneRosterRecord>(
      `/academicSessions/${sessionId}`,
      'academicSession',
    )
  } catch (error) {
    selectedAcademicSessionDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load academic session'
  } finally {
    academicSessionDetailLoading.value = false
  }
}

async function loadTermDetail(termId: string) {
  if (!connected.value || !termId) {
    selectedTermDetail.value = null
    return
  }

  selectedTermDetail.value = null
  termDetailLoading.value = true
  dataError.value = ''

  try {
    selectedTermDetail.value = await fetchRecord<OneRosterRecord>(`/terms/${termId}`, 'term')
  } catch (error) {
    selectedTermDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load term'
  } finally {
    termDetailLoading.value = false
  }
}

async function loadGradingPeriodDetail(gradingPeriodId: string) {
  if (!connected.value || !gradingPeriodId) {
    selectedGradingPeriodDetail.value = null
    return
  }

  selectedGradingPeriodDetail.value = null
  gradingPeriodDetailLoading.value = true
  dataError.value = ''

  try {
    selectedGradingPeriodDetail.value = await fetchRecord<OneRosterRecord>(
      `/gradingPeriods/${gradingPeriodId}`,
      'gradingPeriod',
    )
  } catch (error) {
    selectedGradingPeriodDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load grading period'
  } finally {
    gradingPeriodDetailLoading.value = false
  }
}

async function loadSchoolOrgDetail(schoolId: string) {
  if (!connected.value || !schoolId) {
    selectedSchoolOrgDetail.value = null
    return
  }

  selectedSchoolOrgDetail.value = null
  schoolOrgDetailLoading.value = true
  dataError.value = ''

  try {
    selectedSchoolOrgDetail.value = await fetchRecord<OneRosterRecord>(`/orgs/${schoolId}`, 'org')
  } catch (error) {
    selectedSchoolOrgDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load organization'
  } finally {
    schoolOrgDetailLoading.value = false
  }
}

async function loadSchoolDetail(schoolId: string) {
  if (!connected.value || !schoolId) {
    selectedSchoolDetail.value = null
    return
  }

  selectedSchoolDetail.value = null
  schoolDetailLoading.value = true
  dataError.value = ''

  try {
    selectedSchoolDetail.value = await fetchRecord<OneRosterRecord>(`/schools/${schoolId}`, 'school')
  } catch (error) {
    selectedSchoolDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load school'
  } finally {
    schoolDetailLoading.value = false
  }
}

async function loadClassDetail(classId: string) {
  if (!connected.value || !classId) {
    selectedClassDetail.value = null
    return
  }

  selectedClassDetail.value = null
  classDetailLoading.value = true
  dataError.value = ''

  try {
    selectedClassDetail.value = await fetchRecord<OneRosterRecord>(`/classes/${classId}`, 'class')
  } catch (error) {
    selectedClassDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load class'
  } finally {
    classDetailLoading.value = false
  }
}

async function loadUserDetail(userId: string) {
  if (!connected.value || !userId) {
    selectedUserDetail.value = null
    return
  }

  selectedUserDetail.value = null
  dataError.value = ''

  try {
    selectedUserDetail.value = await fetchRecord<OneRosterRecord>(`/users/${userId}`, 'user')
  } catch (error) {
    selectedUserDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load user'
  }
}

function syncClassEnrollments(classId: string) {
  classEnrollments.value = enrollments.value.filter(
    (enrollment) => getGuidRef(enrollment.class).sourcedId === classId,
  )
  selectedEnrollmentId.value = classEnrollments.value[0]?.sourcedId ?? ''
}

async function loadEnrollmentDetail(enrollmentId: string) {
  if (!connected.value || !enrollmentId) {
    selectedEnrollmentDetail.value = null
    return
  }

  selectedEnrollmentDetail.value = null
  enrollmentDetailLoading.value = true
  dataError.value = ''

  try {
    selectedEnrollmentDetail.value = await fetchRecord<OneRosterRecord>(
      `/enrollments/${enrollmentId}`,
      'enrollment',
    )
  } catch (error) {
    selectedEnrollmentDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load enrollment'
  } finally {
    enrollmentDetailLoading.value = false
  }
}

async function loadPersonDetail() {
  const personId = personMode.value === 'students' ? selectedStudentId.value : selectedTeacherId.value
  if (!connected.value || !personId) {
    selectedPersonDetail.value = null
    return
  }

  selectedPersonDetail.value = null
  personDetailLoading.value = true
  dataError.value = ''

  try {
    selectedPersonDetail.value = await fetchRecord<OneRosterRecord>(
      personMode.value === 'students' ? `/students/${personId}` : `/teachers/${personId}`,
      personMode.value === 'students' ? 'student' : 'teacher',
    )
  } catch (error) {
    selectedPersonDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load person'
  } finally {
    personDetailLoading.value = false
  }
}

async function loadPersonDemographic() {
  const personId = personMode.value === 'students' ? selectedStudentId.value : selectedTeacherId.value
  if (!connected.value || !personId) {
    selectedPersonDemographic.value = null
    return
  }

  if (!demographics.value.some((record) => record.sourcedId === personId)) {
    selectedPersonDemographic.value = null
    return
  }

  personDemographicLoading.value = true
  dataError.value = ''

  try {
    selectedPersonDemographic.value = await fetchRecord<OneRosterRecord>(
      `/demographics/${personId}`,
      'demographic',
    )
  } catch (error) {
    selectedPersonDemographic.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load demographics'
  } finally {
    personDemographicLoading.value = false
  }
}

async function loadSchoolBundle(schoolId: string) {
  if (!connected.value || !schoolId) {
    return
  }

  schoolBundleLoading.value = true
  dataError.value = ''

  try {
    const [loadedCourses, loadedClasses, loadedStudents, loadedTeachers, loadedTerms, loadedEnrollments] = await Promise.all([
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/courses`, 'courses'),
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/classes`, 'classes'),
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/students`, 'students'),
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/teachers`, 'teachers'),
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/terms`, 'terms'),
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/enrollments`, 'enrollments'),
    ])

    schoolCourses.value = loadedCourses
    schoolClasses.value = loadedClasses
    schoolStudents.value = loadedStudents
    schoolTeachers.value = loadedTeachers
    schoolTerms.value = loadedTerms
    schoolEnrollments.value = loadedEnrollments
    selectedSchoolClassId.value = chooseDefaultId(loadedClasses, selectedSchoolClassId.value)
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Unable to load school data'
  } finally {
    schoolBundleLoading.value = false
  }
}

async function loadSchoolClassBundle(schoolId: string, classId: string) {
  if (!connected.value || !schoolId || !classId) {
    schoolClassStudents.value = []
    schoolClassTeachers.value = []
    schoolClassEnrollments.value = []
    return
  }

  schoolClassBundleLoading.value = true
  dataError.value = ''

  try {
    const [loadedEnrollments, loadedStudents, loadedTeachers] = await Promise.all([
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/classes/${classId}/enrollments`, 'enrollments'),
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/classes/${classId}/students`, 'students'),
      fetchCollection<OneRosterRecord>(`/schools/${schoolId}/classes/${classId}/teachers`, 'teachers'),
    ])

    schoolClassEnrollments.value = loadedEnrollments
    schoolClassStudents.value = loadedStudents
    schoolClassTeachers.value = loadedTeachers
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Unable to load school class data'
  } finally {
    schoolClassBundleLoading.value = false
  }
}

async function loadClassBundle(classId: string) {
  if (!connected.value || !classId) {
    classEnrollments.value = []
    selectedEnrollmentId.value = ''
    return
  }

  classBundleLoading.value = true
  dataError.value = ''

  try {
    const [loadedStudents, loadedTeachers, loadedResources, loadedLineItems, loadedResults] = await Promise.all([
      fetchCollection<OneRosterRecord>(`/classes/${classId}/students`, 'students'),
      fetchCollection<OneRosterRecord>(`/classes/${classId}/teachers`, 'teachers'),
      fetchCollection<OneRosterRecord>(`/classes/${classId}/resources`, 'resources'),
      fetchCollection<OneRosterRecord>(`/classes/${classId}/lineItems`, 'lineItems'),
      fetchCollection<OneRosterRecord>(`/classes/${classId}/results`, 'results'),
    ])

    classStudents.value = loadedStudents
    classTeachers.value = loadedTeachers
    classResources.value = loadedResources
    classLineItems.value = loadedLineItems
    classResults.value = loadedResults
    syncClassEnrollments(classId)
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Unable to load class data'
  } finally {
    classBundleLoading.value = false
  }
}

async function loadPersonClasses() {
  const personId = personMode.value === 'students' ? selectedStudentId.value : selectedTeacherId.value
  if (!connected.value || !personId) {
    personClasses.value = []
    return
  }

  personBundleLoading.value = true
  dataError.value = ''

  try {
    personClasses.value = await fetchCollection<OneRosterRecord>(
      personMode.value === 'students' ? `/students/${personId}/classes` : `/teachers/${personId}/classes`,
      'classes',
    )
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Unable to load classes for the selected person'
  } finally {
    personBundleLoading.value = false
  }
}

async function loadUserClasses(userId: string) {
  if (!connected.value || !userId) {
    userClasses.value = []
    return
  }

  dataError.value = ''

  try {
    userClasses.value = await fetchCollection<OneRosterRecord>(`/users/${userId}/classes`, 'classes')
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Unable to load user classes'
  }
}

async function loadTermBundle(termId: string) {
  if (!connected.value || !termId) {
    termClasses.value = []
    termGradingPeriods.value = []
    return
  }

  dataError.value = ''

  try {
    const [loadedClasses, loadedGradingPeriods] = await Promise.all([
      fetchCollection<OneRosterRecord>(`/terms/${termId}/classes`, 'classes'),
      fetchCollection<OneRosterRecord>(`/terms/${termId}/gradingPeriods`, 'gradingPeriods'),
    ])

    termClasses.value = loadedClasses
    termGradingPeriods.value = loadedGradingPeriods
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Unable to load term data'
  }
}

async function loadCourseResources(courseId: string) {
  if (!connected.value || !courseId) {
    courseResources.value = []
    return
  }

  courseResourceLoading.value = true
  dataError.value = ''

  try {
    courseResources.value = await fetchCollection<OneRosterRecord>(
      `/courses/${courseId}/resources`,
      'resources',
    )
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Unable to load course resources'
  } finally {
    courseResourceLoading.value = false
  }
}

async function loadCourseDetail(courseId: string) {
  if (!connected.value || !courseId) {
    selectedCourseDetail.value = null
    return
  }

  selectedCourseDetail.value = null
  courseDetailLoading.value = true
  dataError.value = ''

  try {
    selectedCourseDetail.value = await fetchRecord<OneRosterRecord>(`/courses/${courseId}`, 'course')
  } catch (error) {
    selectedCourseDetail.value = null
    dataError.value = error instanceof Error ? error.message : 'Unable to load course'
  } finally {
    courseDetailLoading.value = false
  }
}

async function loadCourseClasses(courseId: string) {
  if (!connected.value || !courseId) {
    courseClasses.value = []
    return
  }

  dataError.value = ''

  try {
    courseClasses.value = await fetchCollection<OneRosterRecord>(`/courses/${courseId}/classes`, 'classes')
  } catch (error) {
    dataError.value = error instanceof Error ? error.message : 'Unable to load course classes'
  }
}

watch(selectedSchoolId, async (schoolId) => {
  if (schoolId) {
    await Promise.all([loadSchoolBundle(schoolId), loadSchoolDetail(schoolId), loadSchoolOrgDetail(schoolId)])
  } else {
    selectedSchoolDetail.value = null
    selectedSchoolOrgDetail.value = null
    selectedSchoolClassId.value = ''
    schoolEnrollments.value = []
    schoolClassStudents.value = []
    schoolClassTeachers.value = []
    schoolClassEnrollments.value = []
  }
})

watch(selectedAcademicSessionId, async (sessionId) => {
  if (sessionId) {
    await loadAcademicSessionDetail(sessionId)
  } else {
    selectedAcademicSessionDetail.value = null
  }
})

watch(selectedTermId, async (termId) => {
  if (termId) {
    await Promise.all([loadTermDetail(termId), loadTermBundle(termId)])
  } else {
    selectedTermDetail.value = null
    termClasses.value = []
    termGradingPeriods.value = []
  }
})

watch(selectedGradingPeriodId, async (gradingPeriodId) => {
  if (gradingPeriodId) {
    await loadGradingPeriodDetail(gradingPeriodId)
  } else {
    selectedGradingPeriodDetail.value = null
  }
})

watch(selectedClassId, async (classId) => {
  if (classId) {
    await Promise.all([loadClassDetail(classId), loadClassBundle(classId)])
    const selectedClassRecord = selectedClassDetail.value ?? classes.value.find((item) => item.sourcedId === classId) ?? null
    const classSchoolId = getGuidRef(selectedClassRecord?.school).sourcedId
    const classCourseId = getGuidRef(selectedClassRecord?.course).sourcedId

    if (classSchoolId) {
      selectedSchoolId.value = classSchoolId
      selectedSchoolClassId.value = classId
    }

    if (classCourseId) {
      selectedCourseId.value = classCourseId
    }
  } else {
    selectedClassDetail.value = null
    classEnrollments.value = []
    selectedEnrollmentId.value = ''
    selectedEnrollmentDetail.value = null
  }
})

watch([personMode, selectedStudentId, selectedTeacherId], async () => {
  const personId = personMode.value === 'students' ? selectedStudentId.value : selectedTeacherId.value
  await Promise.all([
    loadPersonDetail(),
    loadUserDetail(personId),
    loadUserClasses(personId),
    loadPersonDemographic(),
    loadPersonClasses(),
  ])
})

watch(selectedEnrollmentId, async (enrollmentId) => {
  if (enrollmentId) {
    await loadEnrollmentDetail(enrollmentId)
  } else {
    selectedEnrollmentDetail.value = null
  }
})

watch(selectedCourseId, async (courseId) => {
  if (courseId) {
    await Promise.all([loadCourseDetail(courseId), loadCourseResources(courseId), loadCourseClasses(courseId)])
  } else {
    selectedCourseDetail.value = null
    courseResources.value = []
    courseClasses.value = []
  }
})

watch(selectedSchoolClassId, async (classId) => {
  if (selectedSchoolId.value && classId) {
    await loadSchoolClassBundle(selectedSchoolId.value, classId)
  } else {
    schoolClassStudents.value = []
    schoolClassTeachers.value = []
    schoolClassEnrollments.value = []
  }
})

watch(classStudents, (items) => {
  if (!items.some((item) => item.sourcedId === selectedGradebookStudentId.value)) {
    selectedGradebookStudentId.value = 'all'
  }
})

onMounted(async () => {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl.value)
  if (normalizedBaseUrl !== baseUrl.value) {
    baseUrl.value = normalizedBaseUrl
  }

  if (connected.value) {
    await bootstrapData()
  }
})
</script>

<template>
  <div class="min-h-screen overflow-x-hidden bg-stone-50 text-slate-900">
    <AppHeader :active-view="activeView" :bootstrap-loading="bootstrapLoading" :connected="connected"
      :token-expiry-label="tokenExpiryLabel" :token-loading="tokenLoading" :token-state-label="tokenStateLabel"
      :views="primaryViews" @connect="connectWorkspace" @navigate="activeView = $event"
      @open-settings="connectionSettingsOpen = true" @refresh="refreshWorkspace" />

    <Dialog v-model:open="connectionSettingsOpen">
      <DialogContent class="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Connection Settings</DialogTitle>
          <DialogDescription>
            Point the SPA at your Flask backend and reuse the same client credentials.
          </DialogDescription>
        </DialogHeader>

        <Card class="border-stone-200 bg-stone-50 shadow-none">
          <CardContent class="grid gap-4 pt-6">
            <div class="space-y-2">
              <Label for="base-url">Base URL</Label>
              <Input id="base-url" v-model="baseUrl" />
            </div>
            <div class="space-y-2">
              <Label for="client-id">Client ID</Label>
              <Input id="client-id" v-model="clientId" />
            </div>
            <div class="space-y-2">
              <Label for="client-secret">Client Secret</Label>
              <Input id="client-secret" v-model="clientSecret" type="password" />
            </div>
          </CardContent>
        </Card>
      </DialogContent>
    </Dialog>

    <div class="mx-auto flex min-h-screen max-w-[100rem] min-w-0 flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8 2xl:max-w-[110rem]">
      <Alert v-if="!connected && activeView === 'dashboard'" class="border-sky-200 bg-sky-50 text-sky-950">
        <Sparkles class="h-4 w-4" />
        <AlertTitle>Connect first</AlertTitle>
        <AlertDescription>
          The UI is ready. Press <span class="font-semibold">Connect App</span> to load the OneRoster data into the SPA.
        </AlertDescription>
      </Alert>

      <section v-if="activeView === 'dashboard'"
        class="oneroster-panel rounded-3xl border border-stone-200 bg-white px-6 py-5 shadow-sm lg:px-8">
        <OverviewHub />
      </section>

      <Alert v-if="connectError" class="border-rose-200 bg-rose-50 text-rose-950">
        <Shield class="h-4 w-4" />
        <AlertTitle>Connection error</AlertTitle>
        <AlertDescription>{{ connectError }}</AlertDescription>
      </Alert>

      <Alert v-else-if="dataError" class="border-amber-200 bg-amber-50 text-amber-950">
        <Shield class="h-4 w-4" />
        <AlertTitle>Data warning</AlertTitle>
        <AlertDescription>{{ dataError }}</AlertDescription>
      </Alert>




      <section v-if="activeView === 'dashboard'" class="grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
        <OverviewSnapshots />
      </section>

      <section v-else-if="activeView === 'schools'" class="grid min-w-0 gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
        <Schools />
      </section>

      <section v-else-if="activeView === 'classes'" class="grid min-w-0 gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
        <Classes />
      </section>


      <section v-else-if="activeView === 'people'" class="grid min-w-0 gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
        <People />
      </section>

      <section v-else-if="activeView === 'gradebook'" class="min-w-0 space-y-6">
        <Gradebook />
      </section>

      <section v-else-if="activeView === 'resources'" class="min-w-0 space-y-6">
        <Resources />
      </section>
    </div>
  </div>
</template>
