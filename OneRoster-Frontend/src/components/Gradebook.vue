<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useStorage } from '@vueuse/core'
import { ClipboardList } from '@lucide/vue'

import {
  collectionFromResponse,
  formatDate,
  joinBaseUrl,
  recordTitle,
  type OneRosterRecord,
} from '@/lib/oneroster'
import {
  categories,
  classResults,
  gradebookAverage,
  selectedGradebookStudentId,
} from '@/lib/stores/GradebookStore'
import {
  classBundleLoading,
  classLineItems,
  classes,
  classStudents,
  selectedClassId,
} from '@/lib/stores/ClassesStore'
import { getGuidRef, relatedRecord } from '@/lib/heplers'
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
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const baseUrl = useStorage('oneroster-base-url', '/ims/oneroster/v1p1')
const accessToken = useStorage('oneroster-access-token', '')

const allLineItems = ref<OneRosterRecord[]>([])
const allResults = ref<OneRosterRecord[]>([])
const studentScopedResults = ref<OneRosterRecord[]>([])
const lineItemScopedResults = ref<OneRosterRecord[]>([])

const selectedLineItemId = ref('')
const selectedResultId = ref('')

const selectedCategoryDetail = ref<OneRosterRecord | null>(null)
const selectedLineItemDetail = ref<OneRosterRecord | null>(null)
const selectedResultDetail = ref<OneRosterRecord | null>(null)

const routeLoading = ref(false)
const actionLoading = ref(false)
const gradebookError = ref('')

const categoryTitleDraft = ref('')
const lineItemTitleDraft = ref('')
const lineItemDescriptionDraft = ref('')
const resultScoreDraft = ref('')
const resultCommentDraft = ref('')

const gradebookStudentOptions = computed(() => classStudents.value)
const selectedLineItem = computed(
  () => selectedLineItemDetail.value
    ?? classLineItems.value.find((item) => item.sourcedId === selectedLineItemId.value)
    ?? null,
)
const selectedCategoryId = computed(
  () => getGuidRef(selectedLineItem.value?.category).sourcedId,
)
const visibleResults = computed(() => (
  selectedGradebookStudentId.value === 'all' ? classResults.value : studentScopedResults.value
))

function setDraftsFromDetails() {
  categoryTitleDraft.value = selectedCategoryDetail.value?.title ? String(selectedCategoryDetail.value.title) : ''
  lineItemTitleDraft.value = selectedLineItemDetail.value?.title ? String(selectedLineItemDetail.value.title) : ''
  lineItemDescriptionDraft.value = selectedLineItemDetail.value?.description ? String(selectedLineItemDetail.value.description) : ''
  resultScoreDraft.value = selectedResultDetail.value?.score == null ? '' : String(selectedResultDetail.value.score)
  resultCommentDraft.value = selectedResultDetail.value?.comment ? String(selectedResultDetail.value.comment) : ''
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
    if (typeof record.error === 'string') {
      return record.error
    }
  }

  if (typeof payload === 'string' && payload.trim()) {
    return payload
  }

  return fallback
}

async function requestApi(path: string, init: RequestInit = {}): Promise<unknown> {
  const headers = new Headers({
    Accept: 'application/json',
  })

  if (accessToken.value) {
    headers.set('Authorization', `Bearer ${accessToken.value}`)
  }

  if (init.body) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(joinBaseUrl(baseUrl.value, path), {
    ...init,
    headers,
  })

  const payload = await parsePayload(response)
  if (!response.ok) {
    throw new Error(payloadErrorMessage(payload, `Request failed for ${path}`))
  }

  return payload
}

async function fetchCollection<T extends OneRosterRecord>(path: string, key: string): Promise<T[]> {
  const payload = await requestApi(path)
  return collectionFromResponse<T>(payload, key)
}

async function fetchRecord<T extends OneRosterRecord>(path: string, key: string): Promise<T | null> {
  const payload = await requestApi(path)
  if (!payload || typeof payload !== 'object') {
    return null
  }

  const record = (payload as Record<string, unknown>)[key]
  return record && typeof record === 'object' ? (record as T) : null
}

function replaceRecord(collection: OneRosterRecord[], record: OneRosterRecord): OneRosterRecord[] {
  const index = collection.findIndex((item) => item.sourcedId === record.sourcedId)
  if (index === -1) {
    return [record, ...collection]
  }

  const updated = [...collection]
  updated[index] = record
  return updated
}

function removeRecord(collection: OneRosterRecord[], sourcedId: string): OneRosterRecord[] {
  return collection.filter((item) => item.sourcedId !== sourcedId)
}

async function loadGlobalGradebookCollections() {
  if (!accessToken.value) {
    allLineItems.value = []
    allResults.value = []
    return
  }

  try {
    const [loadedLineItems, loadedResults] = await Promise.all([
      fetchCollection<OneRosterRecord>('/lineItems', 'lineItems'),
      fetchCollection<OneRosterRecord>('/results', 'results'),
    ])

    allLineItems.value = loadedLineItems
    allResults.value = loadedResults
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to load gradebook collections'
  }
}

async function loadCategoryDetail(categoryId: string) {
  if (!categoryId) {
    selectedCategoryDetail.value = null
    categoryTitleDraft.value = ''
    return
  }

  selectedCategoryDetail.value = await fetchRecord<OneRosterRecord>(`/categories/${categoryId}`, 'category')
  setDraftsFromDetails()
}

async function loadLineItemDetail(lineItemId: string) {
  if (!lineItemId) {
    selectedLineItemDetail.value = null
    selectedCategoryDetail.value = null
    lineItemScopedResults.value = []
    lineItemTitleDraft.value = ''
    lineItemDescriptionDraft.value = ''
    return
  }

  const lineItemDetail = await fetchRecord<OneRosterRecord>(`/lineItems/${lineItemId}`, 'lineItem')
  const lineItemClassId = getGuidRef(lineItemDetail?.class).sourcedId

  if (
    lineItemDetail
    && selectedClassId.value
    && lineItemClassId
    && lineItemClassId !== selectedClassId.value
  ) {
    selectedLineItemId.value = ''
    return
  }

  selectedLineItemDetail.value = lineItemDetail
  setDraftsFromDetails()

  const categoryId = getGuidRef(selectedLineItemDetail.value?.category).sourcedId
  await loadCategoryDetail(categoryId)

  if (selectedClassId.value) {
    lineItemScopedResults.value = await fetchCollection<OneRosterRecord>(
      `/classes/${selectedClassId.value}/lineItems/${lineItemId}/results`,
      'results',
    )
  }
}

async function loadResultDetail(resultId: string) {
  if (!resultId) {
    selectedResultDetail.value = null
    resultScoreDraft.value = ''
    resultCommentDraft.value = ''
    return
  }

  selectedResultDetail.value = await fetchRecord<OneRosterRecord>(`/results/${resultId}`, 'result')
  setDraftsFromDetails()
}

async function loadStudentScopedResults() {
  if (!selectedClassId.value || selectedGradebookStudentId.value === 'all') {
    studentScopedResults.value = []
    return
  }

  studentScopedResults.value = await fetchCollection<OneRosterRecord>(
    `/classes/${selectedClassId.value}/students/${selectedGradebookStudentId.value}/results`,
    'results',
  )
}

async function updateCategory() {
  if (!selectedCategoryDetail.value) {
    return
  }

  actionLoading.value = true
  gradebookError.value = ''

  try {
    const payload = await requestApi(`/categories/${selectedCategoryDetail.value.sourcedId}`, {
      method: 'PUT',
      body: JSON.stringify({ title: categoryTitleDraft.value }),
    }) as Record<string, OneRosterRecord | undefined>

    const updated = payload.category
    if (!updated) {
      throw new Error('Category update did not return a category')
    }
    selectedCategoryDetail.value = updated
    categories.value = replaceRecord(categories.value, updated)
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to update category'
  } finally {
    actionLoading.value = false
  }
}

async function deleteCategory() {
  if (!selectedCategoryDetail.value) {
    return
  }

  actionLoading.value = true
  gradebookError.value = ''

  try {
    await requestApi(`/categories/${selectedCategoryDetail.value.sourcedId}`, { method: 'DELETE' })
    categories.value = removeRecord(categories.value, selectedCategoryDetail.value.sourcedId)
    selectedCategoryDetail.value = null
    categoryTitleDraft.value = ''
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to delete category'
  } finally {
    actionLoading.value = false
  }
}

async function updateLineItem() {
  if (!selectedLineItemDetail.value) {
    return
  }

  actionLoading.value = true
  gradebookError.value = ''

  try {
    const payload = await requestApi(`/lineItems/${selectedLineItemDetail.value.sourcedId}`, {
      method: 'PUT',
      body: JSON.stringify({
        title: lineItemTitleDraft.value,
        description: lineItemDescriptionDraft.value,
      }),
    }) as Record<string, OneRosterRecord | undefined>

    const updated = payload.lineItem
    if (!updated) {
      throw new Error('Line item update did not return a line item')
    }
    selectedLineItemDetail.value = updated
    classLineItems.value = replaceRecord(classLineItems.value, updated)
    allLineItems.value = replaceRecord(allLineItems.value, updated)
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to update line item'
  } finally {
    actionLoading.value = false
  }
}

async function deleteLineItem() {
  if (!selectedLineItemDetail.value) {
    return
  }

  actionLoading.value = true
  gradebookError.value = ''

  try {
    const deletedId = selectedLineItemDetail.value.sourcedId
    await requestApi(`/lineItems/${deletedId}`, { method: 'DELETE' })
    classLineItems.value = removeRecord(classLineItems.value, deletedId)
    allLineItems.value = removeRecord(allLineItems.value, deletedId)
    lineItemScopedResults.value = []
    selectedLineItemId.value = classLineItems.value[0]?.sourcedId ?? ''
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to delete line item'
  } finally {
    actionLoading.value = false
  }
}

async function updateResult() {
  if (!selectedResultDetail.value) {
    return
  }

  actionLoading.value = true
  gradebookError.value = ''

  try {
    const payload = await requestApi(`/results/${selectedResultDetail.value.sourcedId}`, {
      method: 'PUT',
      body: JSON.stringify({
        score: resultScoreDraft.value === '' ? null : Number(resultScoreDraft.value),
        comment: resultCommentDraft.value,
      }),
    }) as Record<string, OneRosterRecord | undefined>

    const updated = payload.result
    if (!updated) {
      throw new Error('Result update did not return a result')
    }
    selectedResultDetail.value = updated
    classResults.value = replaceRecord(classResults.value, updated)
    allResults.value = replaceRecord(allResults.value, updated)
    lineItemScopedResults.value = replaceRecord(lineItemScopedResults.value, updated)
    studentScopedResults.value = replaceRecord(studentScopedResults.value, updated)
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to update result'
  } finally {
    actionLoading.value = false
  }
}

async function deleteResult() {
  if (!selectedResultDetail.value) {
    return
  }

  actionLoading.value = true
  gradebookError.value = ''

  try {
    const deletedId = selectedResultDetail.value.sourcedId
    await requestApi(`/results/${deletedId}`, { method: 'DELETE' })
    classResults.value = removeRecord(classResults.value, deletedId)
    allResults.value = removeRecord(allResults.value, deletedId)
    lineItemScopedResults.value = removeRecord(lineItemScopedResults.value, deletedId)
    studentScopedResults.value = removeRecord(studentScopedResults.value, deletedId)
    selectedResultId.value = visibleResults.value[0]?.sourcedId ?? ''
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to delete result'
  } finally {
    actionLoading.value = false
  }
}

watch(accessToken, async (token) => {
  if (token) {
    await loadGlobalGradebookCollections()
  } else {
    allLineItems.value = []
    allResults.value = []
  }
})

watch(
  [selectedClassId, classLineItems],
  async () => {
    const currentId = selectedLineItemId.value
    if (!classLineItems.value.some((item) => item.sourcedId === currentId)) {
      selectedLineItemId.value = classLineItems.value[0]?.sourcedId ?? ''
    }

    if (selectedGradebookStudentId.value !== 'all') {
      try {
        routeLoading.value = true
        gradebookError.value = ''
        await loadStudentScopedResults()
      } catch (error) {
        gradebookError.value = error instanceof Error ? error.message : 'Unable to load student results'
      } finally {
        routeLoading.value = false
      }
    }
  },
  { deep: true },
)

watch(selectedGradebookStudentId, async () => {
  try {
    routeLoading.value = true
    gradebookError.value = ''
    await loadStudentScopedResults()
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to load student results'
  } finally {
    routeLoading.value = false
  }
})

watch(selectedLineItemId, async (lineItemId) => {
  try {
    routeLoading.value = true
    gradebookError.value = ''
    await loadLineItemDetail(lineItemId)
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to load line item detail'
  } finally {
    routeLoading.value = false
  }
})

watch(
  visibleResults,
  (results) => {
    if (!results.some((result) => result.sourcedId === selectedResultId.value)) {
      selectedResultId.value = results[0]?.sourcedId ?? ''
    }
  },
  { deep: true },
)

watch(selectedResultId, async (resultId) => {
  try {
    routeLoading.value = true
    gradebookError.value = ''
    await loadResultDetail(resultId)
  } catch (error) {
    gradebookError.value = error instanceof Error ? error.message : 'Unable to load result detail'
  } finally {
    routeLoading.value = false
  }
})

onMounted(async () => {
  if (accessToken.value) {
    await loadGlobalGradebookCollections()
  }
})
</script>

<template>
  <Card class="border-stone-200 bg-white shadow-sm">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-slate-950">
        <ClipboardList class="h-4 w-4" />
        Gradebook
      </CardTitle>
      <CardDescription>Use a class to inspect line items, scoped results, and selected record actions.</CardDescription>
    </CardHeader>
    <CardContent class="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
      <div class="space-y-2">
        <Label>Class</Label>
        <Select v-model="selectedClassId">
          <SelectTrigger>
            <SelectValue placeholder="Choose class" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="item in classes" :key="item.sourcedId" :value="item.sourcedId">
              {{ recordTitle(item) }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="space-y-2">
        <Label>Student Filter</Label>
        <Select v-model="selectedGradebookStudentId">
          <SelectTrigger>
            <SelectValue placeholder="All students" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All students</SelectItem>
            <SelectItem v-for="student in gradebookStudentOptions" :key="student.sourcedId" :value="student.sourcedId">
              {{ recordTitle(student) }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader class="pb-2">
          <CardDescription>Average Score</CardDescription>
          <CardTitle class="text-2xl text-slate-950">{{ gradebookAverage === null ? 'N/A' : gradebookAverage.toFixed(1) }}</CardTitle>
        </CardHeader>
      </Card>

      <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader class="pb-2">
          <CardDescription>Visible Results</CardDescription>
          <CardTitle class="text-2xl text-slate-950">{{ visibleResults.length }}</CardTitle>
        </CardHeader>
      </Card>

      <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader class="pb-2">
          <CardDescription>All Line Items</CardDescription>
          <CardTitle class="text-2xl text-slate-950">{{ allLineItems.length }}</CardTitle>
        </CardHeader>
      </Card>

      <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader class="pb-2">
          <CardDescription>All Results</CardDescription>
          <CardTitle class="text-2xl text-slate-950">{{ allResults.length }}</CardTitle>
        </CardHeader>
      </Card>
    </CardContent>
  </Card>

  <div v-if="gradebookError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
    {{ gradebookError }}
  </div>

  <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
    <Card class="border-stone-200 bg-white shadow-sm">
      <CardHeader>
        <CardTitle class="text-slate-950">Line Items</CardTitle>
      </CardHeader>
      <CardContent>
        <template v-if="classBundleLoading || routeLoading">
          <div class="space-y-2">
            <Skeleton class="h-12 rounded-xl" v-for="index in 6" :key="index" />
          </div>
        </template>
        <template v-else>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Due</TableHead>
                <TableHead>Range</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="item in classLineItems"
                :key="item.sourcedId"
                class="cursor-pointer"
                :class="selectedLineItemId === item.sourcedId ? 'bg-amber-50' : ''"
                @click="selectedLineItemId = item.sourcedId"
              >
                <TableCell>
                  <div class="font-medium text-slate-950">{{ recordTitle(item) }}</div>
                  <div class="text-xs text-slate-500">{{ item.sourcedId }}</div>
                </TableCell>
                <TableCell>{{ recordTitle(relatedRecord(categories, item.category)) }}</TableCell>
                <TableCell>{{ formatDate(String(item.dueDate || '')) }}</TableCell>
                <TableCell>{{ item.resultValueMin }} - {{ item.resultValueMax }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </template>
      </CardContent>
    </Card>

    <Card class="border-stone-200 bg-white shadow-sm">
      <CardHeader>
        <CardTitle class="text-slate-950">Results</CardTitle>
        <CardDescription>
          {{ selectedGradebookStudentId === 'all' ? 'Class-wide results.' : 'Student-scoped results loaded from the class-student route.' }}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <template v-if="classBundleLoading || routeLoading">
          <div class="space-y-2">
            <Skeleton class="h-12 rounded-xl" v-for="index in 6" :key="index" />
          </div>
        </template>
        <template v-else>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Student</TableHead>
                <TableHead>Line Item</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="result in visibleResults"
                :key="result.sourcedId"
                class="cursor-pointer"
                :class="selectedResultId === result.sourcedId ? 'bg-amber-50' : ''"
                @click="selectedResultId = result.sourcedId"
              >
                <TableCell>{{ recordTitle(relatedRecord(classStudents, result.student)) }}</TableCell>
                <TableCell>{{ recordTitle(relatedRecord(classLineItems, result.lineItem)) }}</TableCell>
                <TableCell>{{ result.scoreStatus }}</TableCell>
                <TableCell>{{ result.score }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </template>
      </CardContent>
    </Card>
  </div>

  <div class="grid gap-6 xl:grid-cols-3">
    <Card class="border-stone-200 bg-white shadow-sm">
      <CardHeader>
        <CardTitle class="text-slate-950">Selected Category</CardTitle>
        <CardDescription>Loaded through the category detail route.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <template v-if="selectedCategoryDetail">
          <div class="space-y-2 text-sm text-slate-700">
            <div><span class="font-semibold text-slate-950">Title:</span> {{ selectedCategoryDetail.title || 'Not set' }}</div>
            <div><span class="font-semibold text-slate-950">ID:</span> {{ selectedCategoryDetail.sourcedId }}</div>
          </div>
          <div class="space-y-2">
            <Label>Category Title</Label>
            <Input v-model="categoryTitleDraft" />
          </div>
          <div class="flex gap-2">
            <Button :disabled="actionLoading" @click="updateCategory">Save Category</Button>
            <Button variant="outline" :disabled="actionLoading" @click="deleteCategory">Delete Category</Button>
          </div>
        </template>
        <div v-else class="text-sm text-slate-500">Select a line item with a category.</div>
      </CardContent>
    </Card>

    <Card class="border-stone-200 bg-white shadow-sm">
      <CardHeader>
        <CardTitle class="text-slate-950">Selected Line Item</CardTitle>
        <CardDescription>Loaded through the line item detail route and class-line-item results route.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <template v-if="selectedLineItemDetail">
          <div class="space-y-2 text-sm text-slate-700">
            <div><span class="font-semibold text-slate-950">Title:</span> {{ selectedLineItemDetail.title || 'Not set' }}</div>
            <div><span class="font-semibold text-slate-950">Due:</span> {{ formatDate(String(selectedLineItemDetail.dueDate || '')) }}</div>
            <div><span class="font-semibold text-slate-950">Category:</span> {{ recordTitle(selectedCategoryDetail) }}</div>
            <div><span class="font-semibold text-slate-950">Scoped Results:</span> {{ lineItemScopedResults.length }}</div>
          </div>
          <div class="space-y-2">
            <Label>Line Item Title</Label>
            <Input v-model="lineItemTitleDraft" />
          </div>
          <div class="space-y-2">
            <Label>Description</Label>
            <Input v-model="lineItemDescriptionDraft" />
          </div>
          <div class="flex gap-2">
            <Button :disabled="actionLoading" @click="updateLineItem">Save Line Item</Button>
            <Button variant="outline" :disabled="actionLoading" @click="deleteLineItem">Delete Line Item</Button>
          </div>
        </template>
        <div v-else class="text-sm text-slate-500">Select a line item from the table.</div>
      </CardContent>
    </Card>

    <Card class="border-stone-200 bg-white shadow-sm">
      <CardHeader>
        <CardTitle class="text-slate-950">Selected Result</CardTitle>
        <CardDescription>Loaded through the single-result route.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <template v-if="selectedResultDetail">
          <div class="space-y-2 text-sm text-slate-700">
            <div><span class="font-semibold text-slate-950">Student:</span> {{ recordTitle(relatedRecord(classStudents, selectedResultDetail.student)) }}</div>
            <div><span class="font-semibold text-slate-950">Line Item:</span> {{ recordTitle(relatedRecord(classLineItems, selectedResultDetail.lineItem)) }}</div>
            <div><span class="font-semibold text-slate-950">Score Date:</span> {{ formatDate(String(selectedResultDetail.scoreDate || '')) }}</div>
            <div><span class="font-semibold text-slate-950">Status:</span> {{ selectedResultDetail.scoreStatus || 'Not set' }}</div>
          </div>
          <div class="space-y-2">
            <Label>Score</Label>
            <Input v-model="resultScoreDraft" type="number" step="0.01" />
          </div>
          <div class="space-y-2">
            <Label>Comment</Label>
            <Input v-model="resultCommentDraft" />
          </div>
          <div class="flex gap-2">
            <Button :disabled="actionLoading" @click="updateResult">Save Result</Button>
            <Button variant="outline" :disabled="actionLoading" @click="deleteResult">Delete Result</Button>
          </div>
        </template>
        <div v-else class="text-sm text-slate-500">Select a result from the table.</div>
      </CardContent>
    </Card>
  </div>
</template>
