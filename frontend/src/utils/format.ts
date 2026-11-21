const guaranies = new Intl.NumberFormat('es-PY', { maximumFractionDigits: 0 })

/** 35000 -> "Gs. 35.000" */
export function formatGs(amount: number): string {
  return `Gs. ${guaranies.format(amount)}`
}

/** A wa.me link from a number like "+595 981 123-456", or null when there's no number. */
export function whatsappLink(number: string, message = ''): string | null {
  const digits = number.replace(/\D/g, '')
  if (!digits) return null
  const text = message ? `?text=${encodeURIComponent(message)}` : ''
  return `https://wa.me/${digits}${text}`
}

/** A tel: link that keeps a leading + and drops spaces and dashes. */
export function telLink(number: string): string {
  return `tel:${number.replace(/[^\d+]/g, '')}`
}
