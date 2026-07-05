<script setup lang="ts">
import { Search } from '@lucide/vue'

import {
  guidRefs,
  recordSubtitle,
  recordTitle,
} from '@/lib/oneroster'
import {
  schoolClasses,
  schoolClassBundleLoading,
  schoolClassEnrollments,
  schoolClassStudents,
  schoolClassTeachers,
  schoolEnrollments,
  orgs,
  schoolOrgDetailLoading,
  schoolOverviewMetrics,
  schoolSearch,
  schoolTeachers,
  filteredSchools,
  selectedSchool,
  selectedSchoolClassId,
  selectedSchoolOrgDetail,
  selectedSchoolId,
} from '@/lib/stores/SchoolsStore'
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
import { Skeleton } from '@/components/ui/skeleton'
import { relatedRecord } from '@/lib/heplers'
</script>

<template>
    <Card class="border-stone-200 bg-white shadow-sm">
        <CardHeader>
        <CardTitle class="flex items-center gap-2 text-slate-950">
            <Search class="h-4 w-4" />
            Schools
        </CardTitle>
        <CardDescription>Choose a school to inspect its courses, classes, and people.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
        <Input v-model="schoolSearch" placeholder="Search schools..." />
        <ScrollArea class="h-[34rem] rounded-2xl border border-slate-200/70 bg-slate-50/70 p-3">
            <div class="space-y-2 pr-3">
            <Button
                v-for="school in filteredSchools"
                :key="school.sourcedId"
                type="button"
                variant="outline"
                class="h-auto w-full justify-start rounded-2xl px-4 py-3 text-left"
                :class="selectedSchoolId === school.sourcedId ? 'border-amber-400 bg-amber-50' : 'bg-white'"
                @click="selectedSchoolId = school.sourcedId"
            >
                <div>
                <div class="font-medium text-slate-950">{{ recordTitle(school) }}</div>
                <div class="text-xs text-slate-500">{{ recordSubtitle(school) || school.sourcedId }}</div>
                </div>
            </Button>
            </div>
        </ScrollArea>
        </CardContent>
    </Card>

    <Card class="border-stone-200 bg-white shadow-sm">
        <CardHeader>
        <CardTitle class="text-slate-950">{{ selectedSchool ? recordTitle(selectedSchool) : 'No school selected' }}</CardTitle>
        <CardDescription>
            {{ selectedSchool ? recordSubtitle(selectedSchool) || selectedSchool.sourcedId : 'Pick a school from the list.' }}
        </CardDescription>
        </CardHeader>
        <CardContent class="space-y-6" v-if="selectedSchool">
        <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Card v-for="metric in schoolOverviewMetrics" :key="metric.label" class="border-slate-200/70 bg-slate-50/70 shadow-none">
            <CardHeader class="pb-2">
                <CardDescription>{{ metric.label }}</CardDescription>
                <CardTitle class="text-2xl text-slate-950">{{ metric.value }}</CardTitle>
            </CardHeader>
            </Card>
        </div>

        <div class="grid gap-5 lg:grid-cols-2">
            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
            <CardHeader>
                <CardTitle class="text-lg">Classes</CardTitle>
            </CardHeader>
            <CardContent class="space-y-2">
                <Button
                v-for="item in schoolClasses.slice(0, 8)"
                :key="item.sourcedId"
                type="button"
                variant="outline"
                class="h-auto w-full justify-start rounded-2xl px-4 py-3 text-left"
                :class="selectedSchoolClassId === item.sourcedId ? 'border-amber-400 bg-amber-50' : 'bg-white'"
                @click="selectedSchoolClassId = item.sourcedId"
                >
                <div>
                  <div class="font-medium text-slate-950">{{ recordTitle(item) }}</div>
                  <div class="text-sm text-slate-500">{{ recordSubtitle(item) || item.sourcedId }}</div>
                </div>
                </Button>
            </CardContent>
            </Card>

            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
            <CardHeader>
                <CardTitle class="text-lg">Teachers</CardTitle>
            </CardHeader>
            <CardContent class="space-y-2">
                <div
                v-for="teacher in schoolTeachers.slice(0, 8)"
                :key="teacher.sourcedId"
                class="rounded-2xl border border-slate-200/70 bg-white px-4 py-3"
                >
                <div class="font-medium text-slate-950">{{ recordTitle(teacher) }}</div>
                <div class="text-sm text-slate-500">{{ teacher.email || teacher.sourcedId }}</div>
                </div>
            </CardContent>
            </Card>
        </div>

        <div class="grid gap-5 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
            <CardHeader>
                <CardTitle class="text-lg">School Enrollment Records</CardTitle>
                <CardDescription>Loaded from the school-level enrollment endpoint.</CardDescription>
            </CardHeader>
            <CardContent class="space-y-2">
                <div
                v-for="enrollment in schoolEnrollments.slice(0, 8)"
                :key="enrollment.sourcedId"
                class="rounded-2xl border border-slate-200/70 bg-white px-4 py-3"
                >
                <div class="font-medium text-slate-950">{{ enrollment.sourcedId }}</div>
                <div class="text-sm text-slate-500">
                    {{ enrollment.role || 'No role' }} - {{ enrollment.beginDate || 'No begin date' }}
                </div>
                </div>
            </CardContent>
            </Card>

            <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
            <CardHeader>
                <CardTitle class="text-lg">Selected School Class Roster</CardTitle>
                <CardDescription>Pick a class above to load its school-scoped enrollments, students, and teachers.</CardDescription>
            </CardHeader>
            <CardContent>
                <template v-if="schoolClassBundleLoading">
                <div class="space-y-2">
                    <Skeleton class="h-12 rounded-xl" v-for="index in 4" :key="index" />
                </div>
                </template>
                <div v-else class="grid gap-3 md:grid-cols-3">
                <Card class="border-slate-200/70 bg-white shadow-none">
                    <CardHeader class="pb-2">
                    <CardDescription>Enrollments</CardDescription>
                    <CardTitle class="text-2xl text-slate-950">{{ schoolClassEnrollments.length }}</CardTitle>
                    </CardHeader>
                </Card>
                <Card class="border-slate-200/70 bg-white shadow-none">
                    <CardHeader class="pb-2">
                    <CardDescription>Students</CardDescription>
                    <CardTitle class="text-2xl text-slate-950">{{ schoolClassStudents.length }}</CardTitle>
                    </CardHeader>
                </Card>
                <Card class="border-slate-200/70 bg-white shadow-none">
                    <CardHeader class="pb-2">
                    <CardDescription>Teachers</CardDescription>
                    <CardTitle class="text-2xl text-slate-950">{{ schoolClassTeachers.length }}</CardTitle>
                    </CardHeader>
                </Card>
                </div>
            </CardContent>
            </Card>
        </div>

        <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
            <CardHeader>
            <CardTitle class="text-lg">Organization Detail</CardTitle>
            <CardDescription>The school record loads from the school endpoint and its hierarchy loads from the org endpoint.</CardDescription>
            </CardHeader>
            <CardContent>
            <template v-if="schoolOrgDetailLoading">
                <div class="space-y-2">
                <Skeleton class="h-12 rounded-xl" v-for="index in 4" :key="index" />
                </div>
            </template>
            <template v-else-if="selectedSchoolOrgDetail">
                <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                <Card class="border-slate-200/70 bg-white shadow-none">
                    <CardHeader class="pb-2">
                    <CardDescription>Org Type</CardDescription>
                    <CardTitle class="text-2xl text-slate-950">{{ selectedSchoolOrgDetail.type || 'Not set' }}</CardTitle>
                    </CardHeader>
                </Card>
                <Card class="border-slate-200/70 bg-white shadow-none">
                    <CardHeader class="pb-2">
                    <CardDescription>Parent</CardDescription>
                    <CardTitle class="text-2xl text-slate-950">{{ selectedSchoolOrgDetail.parent ? recordTitle(relatedRecord(orgs, selectedSchoolOrgDetail.parent)) : 'None' }}</CardTitle>
                    </CardHeader>
                </Card>
                <Card class="border-slate-200/70 bg-white shadow-none">
                    <CardHeader class="pb-2">
                    <CardDescription>Children</CardDescription>
                    <CardTitle class="text-2xl text-slate-950">{{ guidRefs(selectedSchoolOrgDetail.children).length }}</CardTitle>
                    </CardHeader>
                </Card>
                <Card class="border-slate-200/70 bg-white shadow-none">
                    <CardHeader class="pb-2">
                    <CardDescription>Org ID</CardDescription>
                    <CardTitle class="text-lg text-slate-950">{{ selectedSchoolOrgDetail.sourcedId }}</CardTitle>
                    </CardHeader>
                </Card>
                </div>
            </template>
            </CardContent>
        </Card>
        </CardContent>
    </Card>
</template>
