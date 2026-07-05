<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStorage } from '@vueuse/core'
import { Library } from '@lucide/vue'

import {
  joinBaseUrl,
  listOf,
  recordSubtitle,
  recordTitle,
  type OneRosterRecord,
} from '@/lib/oneroster'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
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
  classBundleLoading,
  classes,
  classResources,
  courseClasses,
  courses,
  courseDetailLoading,
  courseResourceLoading,
  selectedClass,
  selectedClassId,
  selectedCourse,
  selectedCourseId,
} from '@/lib/stores/ClassesStore'
import { courseResources, resourceMode } from '@/lib/stores/ResourcesStore'

const baseUrl = useStorage('oneroster-base-url', '/ims/oneroster/v1p1')
const accessToken = useStorage('oneroster-access-token', '')

const selectedResourceId = ref('')
const selectedResourceDetail = ref<OneRosterRecord | null>(null)
const resourceDetailLoading = ref(false)
const resourceError = ref('')

const visibleResources = computed(() => (
  resourceMode.value === 'classes' ? classResources.value : courseResources.value
))

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

async function fetchResourceDetail(resourceId: string) {
  if (!resourceId || !accessToken.value) {
    selectedResourceDetail.value = null
    return
  }

  resourceDetailLoading.value = true
  resourceError.value = ''

  try {
    const response = await fetch(joinBaseUrl(baseUrl.value, `/resources/${resourceId}`), {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${accessToken.value}`,
      },
    })

    const payload = await parsePayload(response)
    if (!response.ok) {
      throw new Error(payloadErrorMessage(payload, `Request failed for /resources/${resourceId}`))
    }

    const record = payload && typeof payload === 'object'
      ? (payload as Record<string, unknown>).resource
      : null

    selectedResourceDetail.value = record && typeof record === 'object'
      ? (record as OneRosterRecord)
      : null
  } catch (error) {
    selectedResourceDetail.value = null
    resourceError.value = error instanceof Error ? error.message : 'Unable to load resource'
  } finally {
    resourceDetailLoading.value = false
  }
}

watch(
  visibleResources,
  (items) => {
    if (!items.some((item) => item.sourcedId === selectedResourceId.value)) {
      selectedResourceId.value = items[0]?.sourcedId ?? ''
    }
  },
  { immediate: true, deep: true },
)

watch(selectedResourceId, async (resourceId) => {
  await fetchResourceDetail(resourceId)
})

</script>

<template>
    <Card class="border-stone-200 bg-white shadow-sm">
        <CardHeader>
        <CardTitle class="flex items-center gap-2 text-slate-950">
            <Library class="h-4 w-4" />
            Resource Browser
        </CardTitle>
        <CardDescription>Browse materials from either the class side or the course side.</CardDescription>
        </CardHeader>
        <CardContent class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div class="flex gap-2">
            <Button :variant="resourceMode === 'classes' ? 'default' : 'outline'" class="flex-1" @click="resourceMode = 'classes'">
            Class Resources
            </Button>
            <Button :variant="resourceMode === 'courses' ? 'default' : 'outline'" class="flex-1" @click="resourceMode = 'courses'">
            Course Resources
            </Button>
        </div>

        <div v-if="resourceMode === 'classes'" class="space-y-2">
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

        <div v-else class="space-y-2">
            <Label>Course</Label>
            <Select v-model="selectedCourseId">
            <SelectTrigger>
                <SelectValue placeholder="Choose course" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem v-for="course in courses" :key="course.sourcedId" :value="course.sourcedId">
                {{ recordTitle(course) }}
                </SelectItem>
            </SelectContent>
            </Select>
        </div>

        <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
            <CardHeader class="pb-2">
            <CardDescription>Visible Resources</CardDescription>
            <CardTitle class="text-2xl text-slate-950">
                {{ visibleResources.length }}
            </CardTitle>
            </CardHeader>
        </Card>
        </CardContent>
    </Card>

    <Card class="border-stone-200 bg-white shadow-sm">
        <CardHeader>
        <CardTitle class="text-slate-950">
            {{ resourceMode === 'classes' ? (selectedClass ? recordTitle(selectedClass) : 'Class resources') : (selectedCourse ? recordTitle(selectedCourse) : 'Course resources') }}
        </CardTitle>
        <CardDescription>
            {{ resourceMode === 'classes'
            ? 'Resources directly linked to the current class.'
            : 'Resources linked to the current course.' }}
        </CardDescription>
        </CardHeader>
        <CardContent>
        <template v-if="classBundleLoading || courseResourceLoading">
            <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            <Skeleton class="h-28 rounded-2xl" v-for="index in 6" :key="index" />
            </div>
        </template>
        <template v-else>
            <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            <div
                v-for="resource in visibleResources"
                :key="resource.sourcedId"
                class="cursor-pointer rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4"
                :class="selectedResourceId === resource.sourcedId ? 'border-amber-400 bg-amber-50' : ''"
                @click="selectedResourceId = resource.sourcedId"
            >
                <div class="font-medium text-slate-950">{{ recordTitle(resource) }}</div>
                <div class="mt-1 text-sm text-slate-500">{{ recordSubtitle(resource) || resource.sourcedId }}</div>
                <div class="mt-3 flex flex-wrap gap-2">
                <Badge v-for="role in listOf<string>(resource.roles)" :key="`${resource.sourcedId}-${role}`" variant="outline">
                    {{ role }}
                </Badge>
                </div>
            </div>
            </div>
        </template>
        </CardContent>
    </Card>

    <Card class="border-stone-200 bg-white shadow-sm">
        <CardHeader>
        <CardTitle class="text-slate-950">Selected Resource</CardTitle>
        <CardDescription>Loaded through the single-resource endpoint.</CardDescription>
        </CardHeader>
        <CardContent>
        <div v-if="resourceError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
            {{ resourceError }}
        </div>
        <template v-else-if="resourceDetailLoading">
            <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Skeleton class="h-24 rounded-2xl" v-for="index in 4" :key="index" />
            </div>
        </template>
        <template v-else-if="selectedResourceDetail">
            <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4">
                <div class="text-sm text-slate-500">Title</div>
                <div class="mt-2 font-medium text-slate-950">{{ recordTitle(selectedResourceDetail) }}</div>
            </div>
            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4">
                <div class="text-sm text-slate-500">Vendor Resource ID</div>
                <div class="mt-2 font-medium text-slate-950">{{ selectedResourceDetail.vendorResourceId || 'Not set' }}</div>
            </div>
            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4">
                <div class="text-sm text-slate-500">Vendor ID</div>
                <div class="mt-2 font-medium text-slate-950">{{ selectedResourceDetail.vendorId || 'Not set' }}</div>
            </div>
            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4">
                <div class="text-sm text-slate-500">Importance</div>
                <div class="mt-2 font-medium text-slate-950">{{ selectedResourceDetail.importance || 'Not set' }}</div>
            </div>
            </div>
        </template>
        <div v-else class="text-sm text-slate-500">Select a resource card to load its full detail.</div>
        </CardContent>
    </Card>

    <Card v-if="resourceMode === 'courses'" class="border-stone-200 bg-white shadow-sm">
        <CardHeader>
        <CardTitle class="text-slate-950">Course Detail</CardTitle>
        <CardDescription>Loaded from the single-course rostering endpoint plus the course-classes route.</CardDescription>
        </CardHeader>
        <CardContent>
        <template v-if="courseDetailLoading || courseResourceLoading">
            <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Skeleton class="h-24 rounded-2xl" v-for="index in 4" :key="index" />
            </div>
        </template>
        <template v-else-if="selectedCourse">
            <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4">
                <div class="text-sm text-slate-500">Course Code</div>
                <div class="mt-2 font-medium text-slate-950">{{ selectedCourse.courseCode || 'Not set' }}</div>
            </div>
            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4">
                <div class="text-sm text-slate-500">Status</div>
                <div class="mt-2 font-medium text-slate-950">{{ selectedCourse.status || 'Not set' }}</div>
            </div>
            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4">
                <div class="text-sm text-slate-500">Classes Teaching It</div>
                <div class="mt-2 font-medium text-slate-950">{{ courseClasses.length }}</div>
            </div>
            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 px-4 py-4">
                <div class="text-sm text-slate-500">Subjects</div>
                <div class="mt-2 font-medium text-slate-950">{{ listOf<string>(selectedCourse.subjects).join(', ') || 'Not set' }}</div>
            </div>
            </div>
        </template>
        </CardContent>
    </Card>
</template>
