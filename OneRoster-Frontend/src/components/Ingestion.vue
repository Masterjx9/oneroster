<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useStorage } from '@vueuse/core'
import { ArrowDownToLine, CloudDownload, Database, FileJson } from '@lucide/vue'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { joinBaseUrl, normalizeBaseUrl } from '@/lib/oneroster'

interface ProviderConfigurationRecord {
  id: number
  name: string
  baseUrl: string
  tokenUrl: string
  clientId: string
  clientSecretConfigured: boolean
  scopes: string[]
  createdAt: string | null
  updatedAt: string | null
}

interface ProviderImportRunRecord {
  id: number
  providerConfigurationId: number
  status: string
  startedAt: string | null
  finishedAt: string | null
  errorMessage: string | null
  counts: Record<string, number>
}

interface ImportedDataResponse {
  providerConfiguration: ProviderConfigurationRecord
  providerImportRun: ProviderImportRunRecord
  resource?: string
  count?: number
  data: Record<string, unknown[]> | unknown[]
}

const REQUIRED_SCOPES = [
  'https://purl.imsglobal.org/spec/or/v1p1/scope/roster-core.readonly',
  'https://purl.imsglobal.org/spec/or/v1p1/scope/roster.readonly',
  'https://purl.imsglobal.org/spec/or/v1p1/scope/roster-demographics.readonly',
]

const RESOURCE_OPTIONS = [
  'all',
  'academicSessions',
  'classes',
  'courses',
  'demographics',
  'enrollments',
  'gradingPeriods',
  'orgs',
  'schools',
  'students',
  'teachers',
  'terms',
  'users',
] as const

const workspaceBaseUrl = useStorage('oneroster-base-url', '/ims/oneroster/v1p1')
const savedConfigId = useStorage('oneroster-ingestion-config-id', '')
const providerName = useStorage('oneroster-ingestion-provider-name', 'OneRoster Provider Copy')
const providerBaseUrl = useStorage('oneroster-ingestion-provider-base-url', '')
const providerTokenUrl = useStorage('oneroster-ingestion-provider-token-url', '')
const providerClientId = useStorage('oneroster-ingestion-provider-client-id', 'oneroster-client')
const providerClientSecret = useStorage('oneroster-ingestion-provider-client-secret', 'oneroster-secret')
const providerScopes = useStorage('oneroster-ingestion-provider-scopes', REQUIRED_SCOPES.join('\n'))

const selectedResource = ref<(typeof RESOURCE_OPTIONS)[number]>('all')
const createLoading = ref(false)
const syncLoading = ref(false)
const readLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const currentConfiguration = ref<ProviderConfigurationRecord | null>(null)
const latestImportRun = ref<ProviderImportRunRecord | null>(null)
const importedDataResponse = ref<ImportedDataResponse | null>(null)

const configIdValue = computed({
  get: () => savedConfigId.value,
  set: (value: string) => {
    savedConfigId.value = value.replace(/\D+/g, '')
  },
})

const apiBaseUrl = computed(() => normalizeBaseUrl(workspaceBaseUrl.value))
const createEndpoint = computed(() => joinBaseUrl(apiBaseUrl.value, '/provider-configurations'))
const syncEndpoint = computed(() =>
  savedConfigId.value
    ? joinBaseUrl(apiBaseUrl.value, `/provider-configurations/${savedConfigId.value}/sync`)
    : `${joinBaseUrl(apiBaseUrl.value, '/provider-configurations')}/{config_id}/sync`,
)
const dataEndpoint = computed(() => {
  const base = savedConfigId.value
    ? joinBaseUrl(apiBaseUrl.value, `/provider-configurations/${savedConfigId.value}/data`)
    : `${joinBaseUrl(apiBaseUrl.value, '/provider-configurations')}/{config_id}/data`

  return selectedResource.value === 'all'
    ? base
    : `${base}?resource=${encodeURIComponent(selectedResource.value)}`
})

const previewJson = computed(() =>
  importedDataResponse.value ? JSON.stringify(importedDataResponse.value, null, 2) : '',
)

const importedSummary = computed(() => {
  const data = importedDataResponse.value?.data

  if (!data) {
    return []
  }

  if (Array.isArray(data)) {
    return [
      {
        key: importedDataResponse.value?.resource ?? selectedResource.value,
        count: data.length,
      },
    ]
  }

  return Object.entries(data).map(([key, value]) => ({
    key,
    count: Array.isArray(value) ? value.length : 0,
  }))
})

function providerBaseFromCurrentWorkspace() {
  const normalized = normalizeBaseUrl(workspaceBaseUrl.value)
  if (/^https?:\/\//i.test(normalized)) {
    return normalized
  }
  return `${window.location.origin}${normalized}`
}

function ensureProviderDefaults() {
  if (!providerBaseUrl.value.trim()) {
    providerBaseUrl.value = providerBaseFromCurrentWorkspace()
  }

  if (!providerTokenUrl.value.trim()) {
    providerTokenUrl.value = `${providerBaseUrl.value.replace(/\/$/, '')}/token`
  }
}

function normalizedScopeList() {
  return providerScopes.value
    .split(/[\s,]+/)
    .map((scope) => scope.trim())
    .filter(Boolean)
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

function payloadErrorMessage(payload: unknown, fallback: string) {
  if (payload && typeof payload === 'object') {
    const record = payload as Record<string, unknown>
    if (typeof record.error === 'string') {
      return record.error
    }
    if (typeof record.error_description === 'string') {
      return record.error_description
    }
  }

  if (typeof payload === 'string' && payload.trim()) {
    return payload
  }

  return fallback
}

function resetMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

async function createConfiguration() {
  createLoading.value = true
  resetMessages()
  ensureProviderDefaults()

  try {
    const response = await fetch(createEndpoint.value, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: providerName.value.trim(),
        baseUrl: providerBaseUrl.value.trim(),
        tokenUrl: providerTokenUrl.value.trim(),
        clientId: providerClientId.value.trim(),
        clientSecret: providerClientSecret.value.trim(),
        scopes: normalizedScopeList(),
      }),
    })

    const payload = await parsePayload(response)
    if (!response.ok || !payload || typeof payload !== 'object') {
      throw new Error(payloadErrorMessage(payload, 'Unable to save provider configuration'))
    }

    const configuration = (payload as { providerConfiguration?: ProviderConfigurationRecord }).providerConfiguration
    if (!configuration) {
      throw new Error('Provider configuration response was missing the saved record.')
    }

    currentConfiguration.value = configuration
    savedConfigId.value = String(configuration.id)
    successMessage.value = `Saved provider configuration ${configuration.id}.`
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to save provider configuration'
  } finally {
    createLoading.value = false
  }
}

async function syncConfiguration() {
  if (!savedConfigId.value) {
    errorMessage.value = 'Save a provider configuration first or enter an existing configuration id.'
    return
  }

  syncLoading.value = true
  resetMessages()

  try {
    const response = await fetch(syncEndpoint.value, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
    })

    const payload = await parsePayload(response)
    if (!response.ok || !payload || typeof payload !== 'object') {
      throw new Error(payloadErrorMessage(payload, 'Unable to sync provider data'))
    }

    const record = payload as {
      providerConfiguration?: ProviderConfigurationRecord
      providerImportRun?: ProviderImportRunRecord
    }

    currentConfiguration.value = record.providerConfiguration ?? currentConfiguration.value
    latestImportRun.value = record.providerImportRun ?? null
    successMessage.value = `Synced configuration ${savedConfigId.value} into the copied local store.`
    await loadImportedData()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to sync provider data'
  } finally {
    syncLoading.value = false
  }
}

async function loadImportedData() {
  if (!savedConfigId.value) {
    errorMessage.value = 'Enter a saved provider configuration id before loading copied data.'
    return
  }

  readLoading.value = true
  resetMessages()

  try {
    const response = await fetch(dataEndpoint.value, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    })

    const payload = await parsePayload(response)
    if (!response.ok || !payload || typeof payload !== 'object') {
      throw new Error(payloadErrorMessage(payload, 'Unable to read copied provider data'))
    }

    const data = payload as ImportedDataResponse
    importedDataResponse.value = data
    currentConfiguration.value = data.providerConfiguration
    latestImportRun.value = data.providerImportRun
    successMessage.value =
      selectedResource.value === 'all'
        ? `Loaded the copied dataset for configuration ${savedConfigId.value}.`
        : `Loaded copied ${selectedResource.value} data for configuration ${savedConfigId.value}.`
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to read copied provider data'
  } finally {
    readLoading.value = false
  }
}

watch(
  () => providerBaseUrl.value,
  (value, previousValue) => {
    if (!providerTokenUrl.value || providerTokenUrl.value === `${previousValue.replace(/\/$/, '')}/token`) {
      providerTokenUrl.value = `${value.replace(/\/$/, '')}/token`
    }
  },
)

onMounted(() => {
  ensureProviderDefaults()
})
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
      <Card class="oneroster-panel border border-stone-200 bg-white shadow-sm">
        <CardHeader>
          <div class="flex items-center gap-3">
            <span class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(90deg,#00f,#55b1e8)] text-white">
              <ArrowDownToLine class="h-5 w-5" />
            </span>
            <div>
              <CardTitle>Ingestion Workflow</CardTitle>
              <CardDescription>
                Save a provider configuration, sync a copied dataset, and read that copied data back through the assignment endpoints.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent class="grid gap-4 text-sm text-slate-700">
          <div class="grid gap-3 sm:grid-cols-3">
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <div class="font-semibold text-slate-950">1. Save config</div>
              <div class="mt-1 text-slate-600">Creates a provider configuration row and returns its database id.</div>
            </div>
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <div class="font-semibold text-slate-950">2. Sync copy</div>
              <div class="mt-1 text-slate-600">Pulls rostering data from that provider and stores a copied snapshot locally.</div>
            </div>
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <div class="font-semibold text-slate-950">3. Read copy</div>
              <div class="mt-1 text-slate-600">Returns the copied local dataset without calling the provider again.</div>
            </div>
          </div>

          <div class="grid gap-3">
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <div class="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">Endpoint 1</div>
              <div class="mt-1 break-all font-mono text-xs text-slate-950">{{ createEndpoint }}</div>
            </div>
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <div class="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">Endpoint 2</div>
              <div class="mt-1 break-all font-mono text-xs text-slate-950">{{ syncEndpoint }}</div>
            </div>
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <div class="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">Endpoint 3</div>
              <div class="mt-1 break-all font-mono text-xs text-slate-950">{{ dataEndpoint }}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card class="oneroster-panel border border-stone-200 bg-white shadow-sm">
        <CardHeader>
          <CardTitle>Provider Configuration</CardTitle>
          <CardDescription>
            This is the OneRoster source your backend will pull from when the sync endpoint runs.
          </CardDescription>
        </CardHeader>
        <CardContent class="grid gap-4">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <Label for="provider-name">Name</Label>
              <Input id="provider-name" v-model="providerName" />
            </div>
            <div class="space-y-2">
              <Label for="config-id">Saved Config ID</Label>
              <Input id="config-id" v-model="configIdValue" placeholder="Created after endpoint 1 runs" />
            </div>
          </div>

          <div class="space-y-2">
            <Label for="provider-base-url">Provider Base URL</Label>
            <Input id="provider-base-url" v-model="providerBaseUrl" />
          </div>

          <div class="space-y-2">
            <Label for="provider-token-url">Provider Token URL</Label>
            <Input id="provider-token-url" v-model="providerTokenUrl" />
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <Label for="provider-client-id">Client ID</Label>
              <Input id="provider-client-id" v-model="providerClientId" />
            </div>
            <div class="space-y-2">
              <Label for="provider-client-secret">Client Secret</Label>
              <Input id="provider-client-secret" v-model="providerClientSecret" type="password" />
            </div>
          </div>

          <div class="space-y-2">
            <Label for="provider-scopes">Scopes</Label>
            <Textarea
              id="provider-scopes"
              v-model="providerScopes"
              class="min-h-28 font-mono text-xs"
            />
          </div>

          <div class="flex flex-wrap gap-2">
            <Button :disabled="createLoading" class="rounded-full" @click="createConfiguration">
              <Database class="mr-2 h-4 w-4" />
              {{ createLoading ? 'Saving...' : 'Save Configuration' }}
            </Button>
            <Badge v-if="currentConfiguration" variant="outline" class="rounded-full px-3 py-1">
              Config {{ currentConfiguration.id }}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </section>

    <Alert v-if="errorMessage" class="border-rose-200 bg-rose-50 text-rose-950">
      <AlertTitle>Ingestion error</AlertTitle>
      <AlertDescription>{{ errorMessage }}</AlertDescription>
    </Alert>

    <Alert v-else-if="successMessage" class="border-emerald-200 bg-emerald-50 text-emerald-950">
      <AlertTitle>Ingestion status</AlertTitle>
      <AlertDescription>{{ successMessage }}</AlertDescription>
    </Alert>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
      <Card class="oneroster-panel border border-stone-200 bg-white shadow-sm">
        <CardHeader>
          <CardTitle>Sync And Readback</CardTitle>
          <CardDescription>
            Run endpoint 2 to copy the provider data locally, then run endpoint 3 to inspect the copied dataset.
          </CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <div class="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">Latest run</div>
              <div class="mt-2 text-lg font-semibold text-slate-950">
                {{ latestImportRun?.status ?? 'Not run yet' }}
              </div>
              <div class="mt-2 text-sm text-slate-600">
                {{ latestImportRun?.finishedAt ?? 'Run endpoint 2 to create a copied dataset.' }}
              </div>
            </div>
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <div class="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">Read filter</div>
              <div class="mt-2">
                <Select v-model="selectedResource">
                  <SelectTrigger>
                    <SelectValue placeholder="All resources" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="option in RESOURCE_OPTIONS" :key="option" :value="option">
                      {{ option }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <Button :disabled="syncLoading || !savedConfigId" class="rounded-full" @click="syncConfiguration">
              <CloudDownload class="mr-2 h-4 w-4" />
              {{ syncLoading ? 'Syncing...' : 'Sync Copied Dataset' }}
            </Button>
            <Button variant="outline" :disabled="readLoading || !savedConfigId" class="rounded-full" @click="loadImportedData">
              <FileJson class="mr-2 h-4 w-4" />
              {{ readLoading ? 'Loading...' : 'Read Copied Data' }}
            </Button>
          </div>

          <div v-if="latestImportRun?.counts && Object.keys(latestImportRun.counts).length" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <div
              v-for="(count, key) in latestImportRun.counts"
              :key="key"
              class="rounded-2xl border border-stone-200 bg-stone-50 p-4"
            >
              <div class="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">{{ key }}</div>
              <div class="mt-1 text-2xl font-semibold text-slate-950">{{ count }}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card class="oneroster-panel border border-stone-200 bg-white shadow-sm">
        <CardHeader>
          <CardTitle>Copied Dataset Preview</CardTitle>
          <CardDescription>
            This is the JSON returned by endpoint 3 after the copied local dataset is read back.
          </CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div v-if="importedSummary.length" class="flex flex-wrap gap-2">
            <Badge
              v-for="summary in importedSummary"
              :key="summary.key"
              variant="outline"
              class="rounded-full px-3 py-1"
            >
              {{ summary.key }}: {{ summary.count }}
            </Badge>
          </div>

          <Textarea
            :model-value="previewJson"
            readonly
            class="min-h-[28rem] font-mono text-xs"
            placeholder="Run the save, sync, and read workflow to inspect the copied dataset JSON here."
          />
        </CardContent>
      </Card>
    </section>
  </div>
</template>
