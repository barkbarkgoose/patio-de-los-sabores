/**
 * Progressive-enhancement helpers for native <dialog> top-layer exit animations
 * and light-dismiss fallback in browsers without `closedby` or discrete display
 * / `overlay` transitions (Firefox and Safari).
 */

let supportsDisplayTransition: boolean | undefined

export function canTransitionDisplay(): boolean {
  if (supportsDisplayTransition !== undefined) return supportsDisplayTransition
  if (
    typeof window === 'undefined' ||
    !window.CSS?.supports?.('transition-behavior', 'allow-discrete') ||
    !document.body
  ) {
    return false
  }
  const probe = document.createElement('div')
  probe.style.cssText = 'transition: display 1s allow-discrete !important; display: block;'
  document.body.appendChild(probe)
  getComputedStyle(probe).display
  probe.style.display = 'none'
  supportsDisplayTransition = getComputedStyle(probe).display === 'block'
  probe.remove()
  return supportsDisplayTransition
}

export function supportsTopLayerExit(): boolean {
  return (
    typeof window !== 'undefined' &&
    Boolean(window.CSS?.supports?.('overlay', 'auto')) &&
    canTransitionDisplay()
  )
}

export async function closeTopLayerDialog(dialog: HTMLDialogElement): Promise<void> {
  if (!dialog.open) return

  if (!supportsTopLayerExit()) {
    if (dialog.hasAttribute('data-closing')) return
    dialog.setAttribute('data-closing', '')
    const animations = dialog.getAnimations({ subtree: true })
    if (animations.length > 0) {
      await Promise.race([
        Promise.allSettled(animations.map((a) => a.finished)),
        new Promise<void>((resolve) => setTimeout(resolve, 600)),
      ])
    }
    if (!dialog.hasAttribute('data-closing')) return
    dialog.removeAttribute('data-closing')
  }

  if (dialog.open) {
    dialog.close()
  }
}

function isOutsideDialog(event: PointerEvent, dialog: HTMLDialogElement): boolean {
  const rect = dialog.getBoundingClientRect()
  return (
    event.clientX < rect.left ||
    event.clientX > rect.right ||
    event.clientY < rect.top ||
    event.clientY > rect.bottom
  )
}

/**
 * Attach light-dismiss fallback when `closedby` is not natively supported (e.g. Safari).
 * Returns a cleanup function to remove listeners.
 */
export function attachLightDismissFallback(
  dialog: HTMLDialogElement,
  onDismiss: () => void
): () => void {
  if (typeof HTMLDialogElement === 'undefined' || 'closedBy' in HTMLDialogElement.prototype) {
    return () => {}
  }

  let pressedOutside = false

  const onPointerDown = (event: PointerEvent) => {
    pressedOutside = isOutsideDialog(event, dialog)
  }

  const onPointerUp = (event: PointerEvent) => {
    if (pressedOutside && isOutsideDialog(event, dialog)) {
      onDismiss()
    }
    pressedOutside = false
  }

  dialog.addEventListener('pointerdown', onPointerDown)
  dialog.addEventListener('pointerup', onPointerUp)

  return () => {
    dialog.removeEventListener('pointerdown', onPointerDown)
    dialog.removeEventListener('pointerup', onPointerUp)
  }
}
