<script setup lang="ts">
import { computed, ref } from 'vue'
import { Menu, RefreshCcw, Wifi, WifiOff } from '@lucide/vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import type { AppView } from '@/lib/oneroster'

interface NavItem {
  value: AppView
  label: string
}

const props = defineProps<{
  activeView: AppView
  bootstrapLoading: boolean
  connected: boolean
  tokenExpiryLabel: string
  tokenLoading: boolean
  tokenStateLabel: string
  views: NavItem[]
}>()

const emit = defineEmits<{
  connect: []
  navigate: [view: AppView]
  openSettings: []
  refresh: []
}>()

const mobileMenuOpen = ref(false)

const connectLabel = computed(() => {
  if (props.tokenLoading) {
    return 'Connecting...'
  }

  return props.connected ? 'Reconnect' : 'Connect'
})

function selectView(view: AppView) {
  emit('navigate', view)
  mobileMenuOpen.value = false
}
</script>

<template>
  <header class="sticky top-0 z-40 border-b border-[rgb(0,0,90)] bg-[rgb(0,0,114)] backdrop-blur">
    <div class="mx-auto flex max-w-[100rem] min-w-0 items-center gap-2 px-4 py-3 sm:px-6 lg:px-8 2xl:max-w-[110rem]">
      <div class="flex min-w-0 flex-1 items-center gap-3 xl:flex-none">
        <Button
          variant="ghost"
          size="icon"
          class="text-white hover:bg-white/10 hover:text-white xl:hidden"
          aria-label="Open navigation"
          @click="mobileMenuOpen = true"
        >
          <Menu class="h-5 w-5" />
        </Button>

        <div class="flex min-w-0 items-center gap-3">
          <div class="inline-flex w-fit shrink-0 rounded-full px-3 py-1">
            <img
              src="/logo.svg"
              alt="1EdTech"
              class="block h-9 w-auto shrink-0 sm:h-10 2xl:h-12"
            >
          </div>
          <span class="max-w-[8.5rem] truncate text-sm font-semibold text-white sm:max-w-[10rem] xl:max-w-[11rem] xl:text-base 2xl:max-w-none 2xl:text-lg">
            Academic Workspace
          </span>
        </div>
      </div>

      <nav class="hidden min-w-0 flex-1 items-center justify-center gap-1 overflow-hidden xl:flex 2xl:gap-2">
        <Button
          v-for="view in views"
          :key="view.value"
          type="button"
          :variant="activeView === view.value ? 'default' : 'ghost'"
          class="rounded-full px-2 text-xs xl:h-8 xl:px-3 2xl:px-4 2xl:text-sm"
          :class="activeView === view.value ? '' : 'text-white hover:bg-white/10 hover:text-white'"
          @click="selectView(view.value)"
        >
          {{ view.label }}
        </Button>
      </nav>

      <div class="ml-auto flex shrink-0 items-center gap-1.5 sm:gap-2">
        <button
          type="button"
          class="hidden min-w-0 rounded-full border border-stone-200 bg-stone-50 px-2.5 py-2 text-left transition hover:border-stone-300 hover:bg-stone-100 xl:flex xl:items-center xl:gap-2"
          @click="$emit('openSettings')"
        >
          <div class="flex items-center gap-2">
            <Wifi v-if="connected" class="h-4 w-4 text-emerald-600" />
            <WifiOff v-else class="h-4 w-4 text-stone-400" />
            <div>
              <div class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-500">
                Connection
              </div>
              <div class="text-xs font-medium text-stone-900 2xl:text-sm">{{ tokenStateLabel }}</div>
            </div>
          </div>

          <div class="hidden 2xl:block">
            <div class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-500">
              Expires
            </div>
            <div class="max-w-44 truncate text-sm text-stone-700">{{ tokenExpiryLabel }}</div>
          </div>
        </button>

        <Button :disabled="tokenLoading || bootstrapLoading" class="rounded-full px-3 text-xs sm:px-4 sm:text-sm" @click="$emit('connect')">
          {{ connectLabel }}
        </Button>

        <Button
          variant="outline"
          class="hidden rounded-full px-3 xl:inline-flex 2xl:px-4"
          :disabled="bootstrapLoading || !connected"
          @click="$emit('refresh')"
        >
          <RefreshCcw class="h-4 w-4 2xl:mr-2" />
          <span class="hidden 2xl:inline">Refresh</span>
        </Button>
      </div>
    </div>

    <Dialog v-model:open="mobileMenuOpen">
      <DialogContent class="w-[calc(100vw-1.5rem)] max-w-[calc(100vw-1.5rem)] p-4 sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Navigate</DialogTitle>
          <DialogDescription>
            Move between schools, classes, people, gradebooks, and resources.
          </DialogDescription>
        </DialogHeader>

        <div class="space-y-4">
          <div class="grid gap-2">
            <Button
              v-for="view in views"
              :key="view.value"
              type="button"
              :variant="activeView === view.value ? 'default' : 'outline'"
              class="justify-start rounded-2xl"
              @click="selectView(view.value)"
            >
              {{ view.label }}
            </Button>
          </div>

          <div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-500">
                  Connection
                </div>
                <div class="mt-1 text-sm font-medium text-stone-900">{{ tokenStateLabel }}</div>
              </div>
              <Badge variant="outline" class="w-fit">{{ connected ? 'Connected' : 'Offline' }}</Badge>
            </div>

            <div class="mt-3 text-sm text-stone-600">{{ tokenExpiryLabel }}</div>

            <div class="mt-4 flex flex-col gap-2 sm:flex-row">
              <Button class="w-full rounded-full sm:flex-1" :disabled="tokenLoading || bootstrapLoading" @click="$emit('connect')">
                {{ connectLabel }}
              </Button>
              <Button
                variant="outline"
                class="w-full rounded-full sm:flex-1"
                :disabled="bootstrapLoading || !connected"
                @click="$emit('refresh')"
              >
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </header>
</template>
