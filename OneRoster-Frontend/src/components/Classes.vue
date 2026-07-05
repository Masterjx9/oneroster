<script setup lang="ts">
import { GraduationCap } from '@lucide/vue'

import {
  formatDate,
  guidRefs,
  listOf,
  recordSubtitle,
  recordTitle,
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
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import {
  classDetailLoading,
  classEnrollments,
  classOverviewMetrics,
  classResources,
  classSearch,
  classStudents,
  classTeachers,
  courseClasses,
  courses,
  enrollmentDetailLoading,
  filteredClasses,
  selectedClass,
  selectedClassId,
  selectedEnrollmentDetail,
  selectedEnrollmentId,
} from '@/lib/stores/ClassesStore'

import {
  schools,
} from '@/lib/stores/SchoolsStore'

import { relatedRecord } from '@/lib/heplers'

</script>


<template>
    <Card class="border-stone-200 bg-white shadow-sm">
    <CardHeader>
    <CardTitle class="flex items-center gap-2 text-slate-950">
        <GraduationCap class="h-4 w-4" />
        Classes
    </CardTitle>
    <CardDescription>Choose a class to inspect its roster, schedule, and resources.</CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
    <Input v-model="classSearch" placeholder="Search classes..." />
    <ScrollArea class="h-[34rem] rounded-2xl border border-slate-200/70 bg-slate-50/70 p-3">
        <div class="space-y-2 pr-3">
        <Button
            v-for="item in filteredClasses"
            :key="item.sourcedId"
            type="button"
            variant="outline"
            class="h-auto w-full justify-start rounded-2xl px-4 py-3 text-left"
            :class="selectedClassId === item.sourcedId ? 'border-amber-400 bg-amber-50' : 'bg-white'"
            @click="selectedClassId = item.sourcedId"
        >
            <div>
            <div class="font-medium text-slate-950">{{ recordTitle(item) }}</div>
            <div class="text-xs text-slate-500">{{ recordSubtitle(item) || item.sourcedId }}</div>
            </div>
        </Button>
        </div>
    </ScrollArea>
    </CardContent>
</Card>

<Card class="border-stone-200 bg-white shadow-sm">
    <CardHeader>
    <CardTitle class="text-slate-950">{{ selectedClass ? recordTitle(selectedClass) : 'No class selected' }}</CardTitle>
    <CardDescription>
        {{ selectedClass ? recordSubtitle(selectedClass) || selectedClass.sourcedId : 'Pick a class from the list.' }}
    </CardDescription>
    </CardHeader>
    <CardContent class="space-y-6" v-if="selectedClass">
    <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Card v-for="metric in classOverviewMetrics" :key="metric.label" class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader class="pb-2">
            <CardDescription>{{ metric.label }}</CardDescription>
            <CardTitle class="text-2xl text-slate-950">{{ metric.value }}</CardTitle>
        </CardHeader>
        </Card>
    </div>

    <div class="grid gap-5 lg:grid-cols-2">
        <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader>
            <CardTitle class="text-lg">Class Details</CardTitle>
        </CardHeader>
        <CardContent class="space-y-3 text-sm text-slate-700">
            <div><span class="font-semibold text-slate-950">Status:</span> {{ selectedClass.status || 'Not set' }}</div>
            <div><span class="font-semibold text-slate-950">Course:</span> {{ recordTitle(relatedRecord(courses, selectedClass.course)) }}</div>
            <div><span class="font-semibold text-slate-950">School:</span> {{ recordTitle(relatedRecord(schools, selectedClass.school)) }}</div>
            <div><span class="font-semibold text-slate-950">Location:</span> {{ selectedClass.location || 'Not set' }}</div>
            <div><span class="font-semibold text-slate-950">Periods:</span> {{ listOf<string>(selectedClass.periods).join(', ') || 'Not set' }}</div>
            <div><span class="font-semibold text-slate-950">Subjects:</span> {{ listOf<string>(selectedClass.subjects).join(', ') || 'Not set' }}</div>
            <div><span class="font-semibold text-slate-950">Grades:</span> {{ listOf<string>(selectedClass.grades).join(', ') || 'Not set' }}</div>
            <div><span class="font-semibold text-slate-950">Terms:</span> {{ guidRefs(selectedClass.terms).map((term) => term.sourcedId).join(', ') || 'Not set' }}</div>
        </CardContent>
        </Card>

        <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader>
            <CardTitle class="text-lg">Roster</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
            <div>
            <div class="mb-2 text-sm font-semibold text-slate-900">Teachers</div>
            <div class="flex flex-wrap gap-2">
                <Badge v-for="teacher in classTeachers" :key="teacher.sourcedId" variant="outline">
                {{ recordTitle(teacher) }}
                </Badge>
            </div>
            </div>
            <Separator />
            <div>
            <div class="mb-2 text-sm font-semibold text-slate-900">Students</div>
            <div class="flex flex-wrap gap-2">
                <Badge v-for="student in classStudents.slice(0, 16)" :key="student.sourcedId" variant="outline">
                {{ recordTitle(student) }}
                </Badge>
            </div>
            </div>
        </CardContent>
        </Card>
    </div>

    <div class="grid gap-5 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader>
            <CardTitle class="text-lg">Enrollment Records</CardTitle>
            <CardDescription>These come from the system enrollment feed for the selected class.</CardDescription>
        </CardHeader>
        <CardContent>
            <ScrollArea class="h-64 rounded-2xl border border-slate-200/70 bg-white p-3">
            <div class="space-y-2 pr-3">
                <Button
                v-for="enrollment in classEnrollments"
                :key="enrollment.sourcedId"
                type="button"
                variant="outline"
                class="h-auto w-full justify-start rounded-2xl px-4 py-3 text-left"
                :class="selectedEnrollmentId === enrollment.sourcedId ? 'border-amber-400 bg-amber-50' : 'bg-white'"
                @click="selectedEnrollmentId = enrollment.sourcedId"
                >
                <div>
                    <div class="font-medium text-slate-950">
                    {{ recordTitle(relatedRecord([...classStudents, ...classTeachers], enrollment.user)) }}
                    </div>
                    <div class="text-xs text-slate-500">
                    {{ enrollment.role || 'No role' }} - {{ enrollment.sourcedId }}
                    </div>
                </div>
                </Button>
            </div>
            </ScrollArea>
        </CardContent>
        </Card>

        <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader>
            <CardTitle class="text-lg">Selected Enrollment</CardTitle>
            <CardDescription>Open the enrollment detail to verify dates, role, and primary teacher status.</CardDescription>
        </CardHeader>
        <CardContent>
            <template v-if="classDetailLoading || enrollmentDetailLoading">
            <div class="space-y-2">
                <Skeleton class="h-14 rounded-2xl" v-for="index in 4" :key="index" />
            </div>
            </template>
            <template v-else-if="selectedEnrollmentDetail">
            <div class="space-y-3 text-sm text-slate-700">
                <div><span class="font-semibold text-slate-950">User:</span> {{ recordTitle(relatedRecord([...classStudents, ...classTeachers], selectedEnrollmentDetail.user)) }}</div>
                <div><span class="font-semibold text-slate-950">Role:</span> {{ selectedEnrollmentDetail.role || 'Not set' }}</div>
                <div><span class="font-semibold text-slate-950">Primary:</span> {{ selectedEnrollmentDetail.primary ?? 'Not set' }}</div>
                <div><span class="font-semibold text-slate-950">Begin Date:</span> {{ formatDate(String(selectedEnrollmentDetail.beginDate || '')) }}</div>
                <div><span class="font-semibold text-slate-950">End Date:</span> {{ formatDate(String(selectedEnrollmentDetail.endDate || '')) }}</div>
                <div><span class="font-semibold text-slate-950">School:</span> {{ recordTitle(relatedRecord(schools, selectedEnrollmentDetail.school)) }}</div>
                <div><span class="font-semibold text-slate-950">Enrollment ID:</span> {{ selectedEnrollmentDetail.sourcedId }}</div>
            </div>
            </template>
            <div v-else class="text-sm text-slate-500">Choose an enrollment record from the list.</div>
        </CardContent>
        </Card>
    </div>

    <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader>
        <CardTitle class="text-lg">Linked Resources</CardTitle>
        </CardHeader>
        <CardContent class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <div
            v-for="resource in classResources"
            :key="resource.sourcedId"
            class="rounded-2xl border border-slate-200/70 bg-white px-4 py-3"
        >
            <div class="font-medium text-slate-950">{{ recordTitle(resource) }}</div>
            <div class="text-sm text-slate-500">{{ recordSubtitle(resource) || resource.sourcedId }}</div>
        </div>
        </CardContent>
    </Card>

    <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
        <CardHeader>
        <CardTitle class="text-lg">Classes Teaching The Same Course</CardTitle>
        <CardDescription>Loaded from the course-to-classes rostering endpoint for this class's course.</CardDescription>
        </CardHeader>
        <CardContent class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <div
            v-for="courseClass in courseClasses"
            :key="courseClass.sourcedId"
            class="rounded-2xl border border-slate-200/70 bg-white px-4 py-3"
        >
            <div class="font-medium text-slate-950">{{ recordTitle(courseClass) }}</div>
            <div class="text-sm text-slate-500">{{ recordSubtitle(courseClass) || courseClass.sourcedId }}</div>
        </div>
        </CardContent>
    </Card>
    </CardContent>
</Card>
</template>
