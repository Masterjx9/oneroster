<script setup lang="ts">
import { computed, ref } from 'vue'
import { Users } from '@lucide/vue'


import {
  personBundleLoading,
  personClasses,
  personDemographicLoading,
  personDetailLoading,
  personMode,
  selectedPersonDemographic,
  selectedPerson,
  selectedUserDetail,
  selectedStudentId,
  selectedTeacherId,
  students,
  teachers,
  demographics,
  userClasses,
  users,
} from '@/lib/stores/PeopleStore'
import { guidRefs, listOf, recordSubtitle, recordTitle, refLabel, formatDate } from '@/lib/oneroster'
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

const activePeople = computed(() => (personMode.value === 'students' ? students.value : teachers.value))

const personSearch = ref('')
const filteredPeople = computed(() => {
  const needle = personSearch.value.trim().toLowerCase()
  if (!needle) {
    return activePeople.value
  }

  return activePeople.value.filter((person) =>
    [recordTitle(person), recordSubtitle(person), person.sourcedId]
      .join(' ')
      .toLowerCase()
      .includes(needle),
  )
})

const activeUserRecord = computed(() => selectedUserDetail.value ?? selectedPerson.value)
</script>
<template>
    <Card class="border-stone-200 bg-white shadow-sm">
          <CardHeader>
            <CardTitle class="flex items-center gap-2 text-slate-950">
              <Users class="h-4 w-4" />
              People
            </CardTitle>
            <CardDescription>Switch between students and teachers and inspect their linked classes and demographics.</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="flex gap-2">
              <Button :variant="personMode === 'students' ? 'default' : 'outline'" class="flex-1" @click="personMode = 'students'">
                Students
              </Button>
              <Button :variant="personMode === 'teachers' ? 'default' : 'outline'" class="flex-1" @click="personMode = 'teachers'">
                Teachers
              </Button>
            </div>
            <Input v-model="personSearch" placeholder="Search people..." />
            <ScrollArea class="h-[34rem] rounded-2xl border border-slate-200/70 bg-slate-50/70 p-3">
              <div class="space-y-2 pr-3">
                <Button
                  v-for="person in filteredPeople"
                  :key="person.sourcedId"
                  type="button"
                  variant="outline"
                  class="h-auto w-full justify-start rounded-2xl px-4 py-3 text-left"
                  :class="(
                    personMode === 'students' ? selectedStudentId : selectedTeacherId
                  ) === person.sourcedId ? 'border-amber-400 bg-amber-50' : 'bg-white'"
                  @click="personMode === 'students' ? selectedStudentId = person.sourcedId : selectedTeacherId = person.sourcedId"
                >
                  <div>
                    <div class="font-medium text-slate-950">{{ recordTitle(person) }}</div>
                    <div class="text-xs text-slate-500">{{ recordSubtitle(person) || person.sourcedId }}</div>
                  </div>
                </Button>
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        <Card class="border-stone-200 bg-white shadow-sm">
          <CardHeader>
            <CardTitle class="text-slate-950">{{ selectedPerson ? recordTitle(selectedPerson) : 'No person selected' }}</CardTitle>
            <CardDescription>
              {{ selectedPerson ? recordSubtitle(selectedPerson) || selectedPerson.sourcedId : 'Pick a person from the list.' }}
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-6" v-if="selectedPerson">
            <div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)]">
              <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader>
                  <CardTitle class="text-lg">Profile</CardTitle>
                  <CardDescription>{{ users.length }} user record{{ users.length === 1 ? '' : 's' }} loaded in the directory.</CardDescription>
                </CardHeader>
                <CardContent class="space-y-3 text-sm text-slate-700">
                  <template v-if="personDetailLoading">
                    <div class="space-y-2">
                      <Skeleton class="h-8 rounded-xl" v-for="index in 5" :key="index" />
                    </div>
                  </template>
                  <template v-else>
                    <div><span class="font-semibold text-slate-950">Username:</span> {{ activeUserRecord?.username || 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">Email:</span> {{ activeUserRecord?.email || 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">Identifier:</span> {{ activeUserRecord?.identifier || 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">Status:</span> {{ activeUserRecord?.status || 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">Role:</span> {{ selectedPerson.role }}</div>
                    <div><span class="font-semibold text-slate-950">Organizations:</span> {{ guidRefs(activeUserRecord?.orgs).map(refLabel).join(', ') || 'Not set' }}</div>
                    <div v-if="personMode === 'students'"><span class="font-semibold text-slate-950">Grades:</span> {{ listOf<string>(selectedPerson.grades).join(', ') || 'Not set' }}</div>
                    <div><span class="font-semibold text-slate-950">User Class Links:</span> {{ userClasses.length }}</div>
                    <div><span class="font-semibold text-slate-950">User ID:</span> {{ activeUserRecord?.sourcedId || selectedPerson.sourcedId }}</div>
                  </template>
                </CardContent>
              </Card>

              <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader>
                  <CardTitle class="text-lg">Linked Classes</CardTitle>
                </CardHeader>
                <CardContent>
                  <template v-if="personBundleLoading">
                    <div class="space-y-2">
                      <Skeleton class="h-14 rounded-2xl" v-for="index in 4" :key="index" />
                    </div>
                  </template>
                  <template v-else>
                    <div class="space-y-2">
                      <div
                        v-for="item in personClasses"
                        :key="item.sourcedId"
                        class="rounded-2xl border border-slate-200/70 bg-white px-4 py-3"
                      >
                        <div class="font-medium text-slate-950">{{ recordTitle(item) }}</div>
                        <div class="text-sm text-slate-500">{{ recordSubtitle(item) || item.sourcedId }}</div>
                      </div>
                    </div>
                  </template>
                </CardContent>
              </Card>

              <Card class="border-slate-200/70 bg-slate-50/70 shadow-none">
                <CardHeader>
                  <CardTitle class="text-lg">Demographics</CardTitle>
                </CardHeader>
                <CardContent>
                  <template v-if="personDemographicLoading">
                    <div class="space-y-2">
                      <Skeleton class="h-8 rounded-xl" v-for="index in 5" :key="index" />
                    </div>
                  </template>
                  <template v-else-if="selectedPersonDemographic">
                    <div class="space-y-3 text-sm text-slate-700">
                      <div><span class="font-semibold text-slate-950">Birth Date:</span> {{ formatDate(String(selectedPersonDemographic.birthDate || '')) }}</div>
                      <div><span class="font-semibold text-slate-950">Sex:</span> {{ selectedPersonDemographic.sex || 'Not set' }}</div>
                      <div><span class="font-semibold text-slate-950">City of Birth:</span> {{ selectedPersonDemographic.cityOfBirth || 'Not set' }}</div>
                      <div><span class="font-semibold text-slate-950">State of Birth:</span> {{ selectedPersonDemographic.stateOfBirthAbbreviation || 'Not set' }}</div>
                      <div><span class="font-semibold text-slate-950">Country of Birth:</span> {{ selectedPersonDemographic.countryOfBirthCode || 'Not set' }}</div>
                      <div><span class="font-semibold text-slate-950">Residence Status:</span> {{ selectedPersonDemographic.publicSchoolResidenceStatus || 'Not set' }}</div>
                    </div>
                  </template>
                  <div v-else class="text-sm text-slate-500">No demographic record is linked to this person.</div>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>
</template>
