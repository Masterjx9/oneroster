<script setup lang="ts">
import { Building2, CalendarRange, ClipboardList } from '@lucide/vue'

import { formatDate, recordSubtitle, recordTitle } from '@/lib/oneroster'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { relatedRecord } from '@/lib/heplers'
import {
  academicSessionDetailLoading,
  academicSessions,
  gradingPeriods,
  gradingPeriodDetailLoading,
  selectedAcademicSession,
  selectedAcademicSessionId,
  selectedGradingPeriod,
  selectedGradingPeriodId,
  selectedTerm,
  selectedTermId,
  termClasses,
  termDetailLoading,
  termGradingPeriods,
  terms,
} from '@/lib/stores/AcademicSessionsStore'

import {
  filteredClassResults,
  gradebookAverage,
} from '@/lib/stores/GradebookStore'

import {
  schoolBundleLoading,
  schoolOverviewMetrics,
  schools,
  schoolCourses,
  selectedSchool,
  selectedSchoolId,
  schoolTerms,
} from '@/lib/stores/SchoolsStore'

import {
  classBundleLoading,
  classes,
  classOverviewMetrics,
  selectedClass,
  selectedClassId,
} from '@/lib/stores/ClassesStore'

function classScoreStatusCount(status: string): number {
  return filteredClassResults.value.filter((result) => result.scoreStatus === status).length
}


</script>

<template>
    <Card class="border-stone-200 bg-white shadow-sm">
        <CardHeader>
        <CardTitle class="flex items-center gap-2 text-slate-950">
            <Building2 class="h-4 w-4" />
            School Snapshot
        </CardTitle>
        <CardDescription>
            {{ selectedSchool ? recordTitle(selectedSchool) : 'Select a school after connecting.' }}
        </CardDescription>
        <div class="pt-2">
            <Select v-model="selectedSchoolId">
            <SelectTrigger>
                <SelectValue placeholder="Choose school" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem v-for="school in schools" :key="school.sourcedId" :value="school.sourcedId">
                {{ recordTitle(school) }}
                </SelectItem>
            </SelectContent>
            </Select>
        </div>
        </CardHeader>
        <CardContent class="space-y-5">
        <template v-if="schoolBundleLoading">
            <div class="grid gap-3 md:grid-cols-2">
            <Skeleton class="h-28 rounded-2xl" v-for="index in 4" :key="index" />
            </div>
        </template>

        <template v-else-if="selectedSchool">
            <div class="grid gap-3 md:grid-cols-2">
            <Card
                v-for="metric in schoolOverviewMetrics"
                :key="metric.label"
                class="border-slate-200/70 bg-slate-50/70 shadow-none"
            >
                <CardHeader class="pb-2">
                <CardDescription>{{ metric.label }}</CardDescription>
                <CardTitle class="text-2xl text-slate-950">{{ metric.value }}</CardTitle>
                </CardHeader>
                <CardContent class="pt-0 text-sm text-slate-600">
                {{ metric.description }}
                </CardContent>
            </Card>
            </div>

            <div class="grid gap-5 lg:grid-cols-2">
            <div class="space-y-3">
                <div class="text-sm font-semibold text-slate-900">Courses</div>
                <div class="space-y-2">
                <div
                    v-for="course in schoolCourses.slice(0, 5)"
                    :key="course.sourcedId"
                    class="rounded-2xl border border-slate-200/70 bg-white px-4 py-3"
                >
                    <div class="font-medium text-slate-950">{{ recordTitle(course) }}</div>
                    <div class="text-sm text-slate-500">{{ course.sourcedId }}</div>
                </div>
                </div>
            </div>

            <div class="space-y-3">
                <div class="text-sm font-semibold text-slate-900">Terms</div>
                <div class="space-y-2">
                <div
                    v-for="term in schoolTerms.slice(0, 5)"
                    :key="term.sourcedId"
                    class="rounded-2xl border border-slate-200/70 bg-white px-4 py-3"
                >
                    <div class="font-medium text-slate-950">{{ recordTitle(term) }}</div>
                    <div class="text-sm text-slate-500">{{ recordSubtitle(term) || term.sourcedId }}</div>
                </div>
                </div>
            </div>
            </div>
        </template>
        </CardContent>
    </Card>

    <Card class="border-stone-200 bg-white shadow-sm">
        <CardHeader>
        <CardTitle class="flex items-center gap-2 text-slate-950">
            <CalendarRange class="h-4 w-4" />
            Academic Calendar
        </CardTitle>
        <CardDescription>
            {{ selectedAcademicSession ? recordTitle(selectedAcademicSession) : 'Select an academic session after connecting.' }}
        </CardDescription>
        <div class="pt-2">
            <Select v-model="selectedAcademicSessionId">
            <SelectTrigger>
                <SelectValue placeholder="Choose academic session" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem v-for="session in academicSessions" :key="session.sourcedId" :value="session.sourcedId">
                {{ recordTitle(session) }}
                </SelectItem>
            </SelectContent>
            </Select>
        </div>
        </CardHeader>
        <CardContent class="space-y-5">
        <template v-if="academicSessionDetailLoading">
            <div class="grid gap-3 md:grid-cols-2">
            <Skeleton class="h-28 rounded-2xl" v-for="index in 4" :key="index" />
            </div>
        </template>

        <template v-else-if="selectedAcademicSession">
            <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader class="items-center pb-2 text-center">
                <CardDescription>Type</CardDescription>
                <CardTitle class="max-w-full break-words text-sm leading-tight text-slate-950 xl:text-base">{{ selectedAcademicSession.type || 'Not set' }}</CardTitle>
                </CardHeader>
            </Card>
            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader class="items-center pb-2 text-center">
                <CardDescription>School Year</CardDescription>
                <CardTitle class="text-lg leading-tight text-slate-950 xl:text-xl">{{ selectedAcademicSession.schoolYear || 'Not set' }}</CardTitle>
                </CardHeader>
            </Card>
            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader class="items-center pb-2 text-center">
                <CardDescription>Start</CardDescription>
                <CardTitle class="text-base leading-tight text-slate-950 xl:text-lg">{{ formatDate(selectedAcademicSession.startDate) }}</CardTitle>
                </CardHeader>
            </Card>
            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader class="items-center pb-2 text-center">
                <CardDescription>End</CardDescription>
                <CardTitle class="text-base leading-tight text-slate-950 xl:text-lg">{{ formatDate(selectedAcademicSession.endDate) }}</CardTitle>
                </CardHeader>
            </Card>
            </div>

            <div class="grid gap-5 lg:grid-cols-2">
            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader>
                <CardTitle class="text-lg">Session Details</CardTitle>
                </CardHeader>
                <CardContent class="space-y-3 text-sm text-slate-700">
                <div><span class="font-semibold text-slate-950">Title:</span> {{ recordTitle(selectedAcademicSession) }}</div>
                <div><span class="font-semibold text-slate-950">Status:</span> {{ selectedAcademicSession.status || 'Not set' }}</div>
                <div><span class="font-semibold text-slate-950">Sourced ID:</span> {{ selectedAcademicSession.sourcedId }}</div>
                <div><span class="font-semibold text-slate-950">Parent:</span> {{ selectedAcademicSession.parent ? recordTitle(relatedRecord(academicSessions, selectedAcademicSession.parent)) : 'None' }}</div>
                </CardContent>
            </Card>

            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader>
                <CardTitle class="text-lg">Child Sessions</CardTitle>
                </CardHeader>
                <CardContent>
                <div v-if="selectedAcademicSession.children?.length" class="flex flex-wrap gap-2">
                    <Badge
                    v-for="child in selectedAcademicSession.children"
                    :key="child.sourcedId"
                    variant="outline"
                    >
                    {{ recordTitle(relatedRecord(academicSessions, child)) }}
                    </Badge>
                </div>
                <div v-else class="text-sm text-slate-500">No child sessions linked.</div>
                </CardContent>
            </Card>
            </div>

            <div class="grid gap-5 lg:grid-cols-2">
            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader>
                <CardTitle class="text-lg">Term Detail</CardTitle>
                <div class="pt-2">
                    <Select v-model="selectedTermId">
                    <SelectTrigger>
                        <SelectValue placeholder="Choose term" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem v-for="term in terms" :key="term.sourcedId" :value="term.sourcedId">
                        {{ recordTitle(term) }}
                        </SelectItem>
                    </SelectContent>
                    </Select>
                </div>
                </CardHeader>
                <CardContent>
                <template v-if="termDetailLoading">
                    <div class="space-y-2">
                    <Skeleton class="h-12 rounded-xl" v-for="index in 4" :key="index" />
                    </div>
                </template>
                <template v-else-if="selectedTerm">
                    <div class="space-y-3 text-sm text-slate-700">
                    <div><span class="font-semibold text-slate-950">Title:</span> {{ recordTitle(selectedTerm) }}</div>
                    <div><span class="font-semibold text-slate-950">Status:</span> {{ selectedTerm.status || 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">School Year:</span> {{ selectedTerm.schoolYear || 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">Start:</span> {{ formatDate(selectedTerm.startDate) }}</div>
                    <div><span class="font-semibold text-slate-950">End:</span> {{ formatDate(selectedTerm.endDate) }}</div>
                    <div><span class="font-semibold text-slate-950">Classes:</span> {{ termClasses.length }}</div>
                    <div><span class="font-semibold text-slate-950">Grading Periods:</span> {{ termGradingPeriods.length }}</div>
                    </div>
                </template>
                </CardContent>
            </Card>

            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader>
                <CardTitle class="text-lg">Grading Period Detail</CardTitle>
                <div class="pt-2">
                    <Select v-model="selectedGradingPeriodId">
                    <SelectTrigger>
                        <SelectValue placeholder="Choose grading period" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem v-for="period in gradingPeriods" :key="period.sourcedId" :value="period.sourcedId">
                        {{ recordTitle(period) }}
                        </SelectItem>
                    </SelectContent>
                    </Select>
                </div>
                </CardHeader>
                <CardContent>
                <template v-if="gradingPeriodDetailLoading">
                    <div class="space-y-2">
                    <Skeleton class="h-12 rounded-xl" v-for="index in 4" :key="index" />
                    </div>
                </template>
                <template v-else-if="selectedGradingPeriod">
                    <div class="space-y-3 text-sm text-slate-700">
                    <div><span class="font-semibold text-slate-950">Title:</span> {{ recordTitle(selectedGradingPeriod) }}</div>
                    <div><span class="font-semibold text-slate-950">Status:</span> {{ selectedGradingPeriod.status || 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">Term:</span> {{ selectedGradingPeriod.parent ? recordTitle(relatedRecord(terms, selectedGradingPeriod.parent)) : 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">Start:</span> {{ formatDate(selectedGradingPeriod.startDate) }}</div>
                    <div><span class="font-semibold text-slate-950">End:</span> {{ formatDate(selectedGradingPeriod.endDate) }}</div>
                    </div>
                </template>
                </CardContent>
            </Card>
            </div>
        </template>
        </CardContent>
    </Card>

    <Card class="border-stone-200 bg-white shadow-sm xl:col-span-2 xl:mx-auto xl:w-full xl:max-w-4xl">
        <CardHeader>
        <CardTitle class="flex items-center gap-2 text-slate-950">
            <ClipboardList class="h-4 w-4" />
            Class Snapshot
        </CardTitle>
        <CardDescription>
            {{ selectedClass ? recordTitle(selectedClass) : 'Select a class after connecting.' }}
        </CardDescription>
        <div class="pt-2">
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
        </CardHeader>
        <CardContent class="space-y-5">
        <template v-if="classBundleLoading">
            <div class="grid gap-3 md:grid-cols-2">
            <Skeleton class="h-28 rounded-2xl" v-for="index in 4" :key="index" />
            </div>
        </template>

        <template v-else-if="selectedClass">
            <div class="grid gap-3 md:grid-cols-2">
            <Card
                v-for="metric in classOverviewMetrics"
                :key="metric.label"
                class="border-slate-200/70 bg-slate-50/70 shadow-none"
            >
                <CardHeader class="pb-2">
                <CardDescription>{{ metric.label }}</CardDescription>
                <CardTitle class="text-2xl text-slate-950">{{ metric.value }}</CardTitle>
                </CardHeader>
                <CardContent class="pt-0 text-sm text-slate-600">
                {{ metric.description }}
                </CardContent>
            </Card>
            </div>

            <div class="rounded-2xl border border-slate-200/70 bg-slate-50/70 p-4">
            <div class="text-sm font-semibold text-slate-900">Gradebook Summary</div>
            <div class="mt-3 flex flex-wrap gap-2">
                <Badge variant="outline">Average: {{ gradebookAverage === null ? 'N/A' : gradebookAverage.toFixed(1) }}</Badge>
                <Badge variant="outline">Fully graded: {{ classScoreStatusCount('fully graded') }}</Badge>
                <Badge variant="outline">Submitted: {{ classScoreStatusCount('submitted') }}</Badge>
                <Badge variant="outline">Not submitted: {{ classScoreStatusCount('not submitted') }}</Badge>
            </div>
            </div>
        </template>
        </CardContent>
    </Card>
</template>
