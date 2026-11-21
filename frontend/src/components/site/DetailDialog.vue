<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useId, watch } from 'vue'
import type { GalleryPhoto, MenuItem } from '@/types/site'
import { attachLightDismissFallback, closeTopLayerDialog } from '@/utils/dialogMotion'
import { formatGs, whatsappLink } from '@/utils/format'
import type { CategoryAccent } from '@/utils/menuTheme'

export type DetailSelection =
  | {
      kind: 'dish'
      item: MenuItem
      categoryName?: string
      accent?: CategoryAccent
    }
  | {
      kind: 'photo'
      photo: GalleryPhoto
    }

interface Props {
  detail: DetailSelection | null
  restaurantName: string
  whatsappNumber?: string
}

interface Emits {
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  whatsappNumber: '',
})

const emit = defineEmits<Emits>()

const dialogRef = ref<HTMLDialogElement | null>(null)
const titleId = useId()
let cleanupLightDismiss: (() => void) | null = null

const dishWhatsappHref = computed(() => {
  if (!props.detail || props.detail.kind !== 'dish' || !props.whatsappNumber) return null
  return whatsappLink(
    props.whatsappNumber,
    `¡Hola ${props.restaurantName}! Quería consultar por "${props.detail.item.name}".`
  )
})

const dialogAccent = computed<CategoryAccent>(() => {
  if (props.detail?.kind === 'dish' && props.detail.accent) return props.detail.accent
  return 'terracota'
})

function requestClose() {
  const dialog = dialogRef.value
  if (dialog) {
    void closeTopLayerDialog(dialog)
  }
}

function onCancel(event: Event) {
  event.preventDefault()
  requestClose()
}

function onNativeClose() {
  const dialog = dialogRef.value
  if (dialog) {
    dialog.returnValue = ''
  }
  emit('close')
}

watch(
  () => props.detail,
  async (next) => {
    const dialog = dialogRef.value
    if (!dialog) return

    if (next) {
      await nextTick()
      if (!dialog.open) {
        dialog.showModal()
      }
    } else if (dialog.open) {
      void closeTopLayerDialog(dialog)
    }
  }
)

onMounted(() => {
  const dialog = dialogRef.value
  if (dialog) {
    cleanupLightDismiss = attachLightDismissFallback(dialog, requestClose)
    if (props.detail && !dialog.open) {
      dialog.showModal()
    }
  }
})

onBeforeUnmount(() => {
  cleanupLightDismiss?.()
})
</script>

<template>
  <dialog
    ref="dialogRef"
    v-bind="{ closedby: 'any' }"
    class="detail-dialog"
    :class="{ 'detail-dialog--photo': detail?.kind === 'photo' }"
    :data-accent="dialogAccent"
    :aria-labelledby="titleId"
    @cancel="onCancel"
    @close="onNativeClose"
  >
    <div v-if="detail" class="detail-dialog__surface">
      <div class="detail-dialog__handle" aria-hidden="true" />

      <button
        type="button"
        class="detail-dialog__close"
        aria-label="Cerrar"
        autofocus
        @click="requestClose"
      >
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 6l12 12M18 6L6 18" />
        </svg>
      </button>

      <template v-if="detail.kind === 'dish'">
        <div class="detail-dialog__media-wrap">
          <img
            v-if="detail.item.photo"
            :src="detail.item.photo"
            :alt="detail.item.name"
            class="detail-dialog__media"
          />
          <div v-else class="detail-dialog__placeholder" aria-hidden="true">
            <svg class="h-14 w-14" viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z"
              />
            </svg>
          </div>
        </div>

        <div class="detail-dialog__body">
          <div class="detail-dialog__badges">
            <span v-if="detail.categoryName" class="detail-dialog__category">
              {{ detail.categoryName }}
            </span>
            <span v-if="!detail.item.is_available" class="badge badge--unavailable">
              <span aria-hidden="true">✕</span>
              <span>Agotado</span>
            </span>
            <span v-else-if="detail.item.is_featured" class="badge badge--featured">
              <span aria-hidden="true">★</span>
              <span>Favorito de la casa</span>
            </span>
          </div>

          <h2 :id="titleId" class="detail-dialog__title">{{ detail.item.name }}</h2>

          <p class="detail-dialog__price">{{ formatGs(detail.item.price) }}</p>

          <p v-if="detail.item.description" class="detail-dialog__description">
            {{ detail.item.description }}
          </p>

          <div class="detail-dialog__actions">
            <a
              v-if="dishWhatsappHref && detail.item.is_available"
              :href="dishWhatsappHref"
              target="_blank"
              rel="noopener"
              class="btn btn--whatsapp flex-1"
            >
              Consultar por WhatsApp
            </a>
            <button type="button" class="btn btn--soft" @click="requestClose">
              Volver al menú
            </button>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="detail-dialog__photo-stage">
          <img
            :src="detail.photo.image"
            :alt="detail.photo.caption || restaurantName"
            class="detail-dialog__photo"
          />
        </div>
        <div class="detail-dialog__photo-bar">
          <h2 :id="titleId" class="detail-dialog__photo-caption">
            {{ detail.photo.caption || restaurantName }}
          </h2>
          <button type="button" class="btn btn--soft" @click="requestClose">
            Cerrar
          </button>
        </div>
      </template>
    </div>
  </dialog>
</template>
