export const ROSTER_CORE_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/roster-core.readonly"
export const ROSTER_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/roster.readonly"
export const ROSTER_DEMOGRAPHICS_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/roster-demographics.readonly"
export const RESOURCE_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/resource.readonly"
export const GRADEBOOK_READONLY_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly"
export const GRADEBOOK_CREATEPUT_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput"
export const GRADEBOOK_DELETE_SCOPE = "https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.delete"

export const ALL_SCOPES = [
  ROSTER_CORE_READONLY_SCOPE,
  ROSTER_READONLY_SCOPE,
  ROSTER_DEMOGRAPHICS_READONLY_SCOPE,
  RESOURCE_READONLY_SCOPE,
  GRADEBOOK_READONLY_SCOPE,
  GRADEBOOK_CREATEPUT_SCOPE,
  GRADEBOOK_DELETE_SCOPE,
] as const

export type AppView = 'dashboard' | 'schools' | 'classes' | 'people' | 'gradebook' | 'resources' | 'ingestion'
export type PersonMode = 'students' | 'teachers'
export type ResourceMode = 'classes' | 'courses'

export interface GuidRef {
  href: string
  sourcedId: string
  type: string
}

export interface OneRosterRecord {
  sourcedId: string
  status?: string
  dateLastModified?: string
  title?: string
  name?: string
  type?: string
  classCode?: string
  courseCode?: string
  username?: string
  givenName?: string
  familyName?: string
  identifier?: string
  email?: string
  role?: string
  primary?: string | boolean | null
  location?: string
  importance?: string
  vendorResourceId?: string
  description?: string
  startDate?: string
  endDate?: string
  beginDate?: string | null
  birthDate?: string | null
  score?: number
  scoreStatus?: string
  scoreDate?: string
  comment?: string
  assignDate?: string
  dueDate?: string
  resultValueMin?: number
  resultValueMax?: number
  sex?: string | null
  cityOfBirth?: string | null
  stateOfBirthAbbreviation?: string | null
  countryOfBirthCode?: string | null
  publicSchoolResidenceStatus?: string | null
  grades?: string[]
  subjects?: string[]
  subjectCodes?: string[]
  periods?: string[]
  roles?: string[]
  orgs?: GuidRef[]
  agents?: GuidRef[]
  parent?: GuidRef | null
  children?: GuidRef[]
  course?: GuidRef
  school?: GuidRef
  terms?: GuidRef[]
  resources?: GuidRef[]
  org?: GuidRef
  schoolYear?: GuidRef | string | null
  user?: GuidRef
  class?: GuidRef
  category?: GuidRef
  gradingPeriod?: GuidRef
  lineItem?: GuidRef
  student?: GuidRef
  [key: string]: unknown
}

export interface TokenPayload {
  access_token: string
  expires_in?: number
  token_type?: string
  scope?: string
}

export const SAMPLE_IDS = {
  school: 'ORG_1',
  class: 'CLASS_001',
  course: 'COURSE_001',
  student: 'USER_001',
  teacher: 'USER_0',
}

export const ONEROSTER_API_PREFIX = '/ims/oneroster/v1p1'

export const VIEW_OPTIONS: Array<{ value: AppView; label: string; description: string }> = [
  { value: 'dashboard', label: 'Overview', description: 'High-level academic snapshot.' },
  { value: 'schools', label: 'Schools', description: 'School-level classes, people, and terms.' },
  { value: 'classes', label: 'Classes', description: 'Roster, schedule, and linked resources.' },
  { value: 'people', label: 'People', description: 'Students and teachers across the system.' },
  { value: 'gradebook', label: 'Gradebook', description: 'Line items and results by class.' },
  { value: 'resources', label: 'Resources', description: 'Course and class learning materials.' },
  { value: 'ingestion', label: 'Ingestion', description: 'Save provider configs, sync copied data, and inspect imports.' },
] as const

export interface MetricCard {
  label: string
  value: string | number
  description: string
}

export function joinBaseUrl(baseUrl: string, path: string): string {
  return `${normalizeBaseUrl(baseUrl)}${path}`
}

export function normalizeBaseUrl(baseUrl: string): string {
  const trimmedBase = baseUrl.trim()
  if (!trimmedBase || trimmedBase === '/') {
    return ONEROSTER_API_PREFIX
  }

  const withoutTrailingSlash = trimmedBase.endsWith('/') ? trimmedBase.slice(0, -1) : trimmedBase
  if (withoutTrailingSlash.endsWith(ONEROSTER_API_PREFIX)) {
    return withoutTrailingSlash
  }

  if (withoutTrailingSlash.endsWith('/ims/oneroster')) {
    return `${withoutTrailingSlash}/v1p1`
  }

  if (/^https?:\/\//i.test(withoutTrailingSlash)) {
    return `${withoutTrailingSlash}${ONEROSTER_API_PREFIX}`
  }

  if (withoutTrailingSlash === '/ims/oneroster') {
    return ONEROSTER_API_PREFIX
  }

  if (withoutTrailingSlash.startsWith('/')) {
    return `${withoutTrailingSlash}${ONEROSTER_API_PREFIX}`
  }

  return `/${withoutTrailingSlash}${ONEROSTER_API_PREFIX}`
}

export function listOf<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : []
}

export function guidRefs(value: unknown): GuidRef[] {
  return listOf<GuidRef>(value)
}

export function recordTitle(record: OneRosterRecord | null | undefined): string {
  if (!record) {
    return 'Unknown record'
  }

  if (record.title) {
    return record.title
  }

  if (record.name) {
    return record.name
  }

  if (record.givenName || record.familyName) {
    return [record.givenName, record.familyName].filter(Boolean).join(' ')
  }

  if (record.vendorResourceId) {
    return record.vendorResourceId
  }

  if (record.username) {
    return record.username
  }

  return record.sourcedId
}

export function recordSubtitle(record: OneRosterRecord | null | undefined): string {
  if (!record) {
    return ''
  }

  return [
    record.classCode,
    record.courseCode,
    record.type,
    record.identifier,
    record.email,
    record.location,
    record.importance,
    record.scoreStatus,
  ]
    .filter((value): value is string => Boolean(value))
    .join(' • ')
}

export function refLabel(ref: GuidRef | null | undefined): string {
  return ref?.sourcedId ?? 'None'
}

export function average(values: Array<number | null | undefined>): number | null {
  const valid = values.filter((value): value is number => typeof value === 'number' && !Number.isNaN(value))
  if (!valid.length) {
    return null
  }

  return valid.reduce((sum, value) => sum + value, 0) / valid.length
}

export function formatDate(value: string | null | undefined): string {
  if (!value) {
    return 'Not set'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleDateString()
}

export function collectionFromResponse<T>(payload: unknown, key: string): T[] {
  if (!payload || typeof payload !== 'object') {
    return []
  }

  const record = payload as Record<string, unknown>
  return listOf<T>(record[key])
}
