<script setup lang="ts">
import { computed } from 'vue'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { recordTitle, type MetricCard } from '@/lib/oneroster'
import { academicSessions } from '@/lib/stores/AcademicSessionsStore'
import { gradebookAverage } from '@/lib/stores/GradebookStore'
import { classes, selectedClass } from '@/lib/stores/ClassesStore'
import { students, teachers } from '@/lib/stores/PeopleStore'
import { resources } from '@/lib/stores/ResourcesStore'
import { schools } from '@/lib/stores/SchoolsStore'

const dashboardMetrics = computed<MetricCard[]>(() => [
  {
    label: 'Schools',
    value: schools.value.length,
    description: 'Campus organizations of type school.',
  },
  {
    label: 'Classes',
    value: classes.value.length,
    description: 'Scheduled classes currently loaded.',
  },
  {
    label: 'Sessions',
    value: academicSessions.value.length,
    description: 'Academic sessions across terms and grading periods.',
  },
  {
    label: 'Students',
    value: students.value.length,
    description: 'Student records available to browse.',
  },
  {
    label: 'Teachers',
    value: teachers.value.length,
    description: 'Teacher records available to browse.',
  },
  {
    label: 'Resources',
    value: resources.value.length,
    description: 'Learning materials linked to classes or courses.',
  },
  {
    label: 'Class Average',
    value: gradebookAverage.value === null ? 'N/A' : gradebookAverage.value.toFixed(1),
    description: selectedClass.value ? `From ${recordTitle(selectedClass.value)}` : 'Select a class for gradebook metrics.',
  },
])


</script>


<template>
    <div class="mx-auto w-full max-w-5xl">
        <div class="space-y-2">
        <div class="space-y-1">
            <h1 class="text-3xl font-semibold tracking-[-0.03em] text-slate-950">
            1EdTech OneRoster® Operations Hub
            </h1>
            <p class="max-w-3xl text-sm leading-5 text-slate-600">
            Browse schools, classes, people, gradebooks, and resources from one workspace.
            </p>
        </div>

        <section class="flex flex-wrap justify-center gap-2 xl:flex-nowrap">
            <Card
            v-for="metric in dashboardMetrics"
            :key="metric.label"
            class="w-full max-w-[150px] border-stone-200 bg-white shadow-sm text-center"
            >
            <CardHeader class="px-4 pb-1 pt-3">
                <CardDescription class="text-[0.72rem]">{{ metric.label }}</CardDescription>
                <CardTitle class="text-xl leading-none text-slate-950">{{ metric.value }}</CardTitle>
            </CardHeader>
            <CardContent class="px-4 pb-3 pt-0 text-[0.72rem] leading-4 text-slate-600">
                {{ metric.description }}
            </CardContent>
            </Card>
        </section>
        </div>
    </div>
</template>
