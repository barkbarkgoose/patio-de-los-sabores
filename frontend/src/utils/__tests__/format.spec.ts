import { describe, expect, it } from 'vitest'
import { formatGs, telLink, whatsappLink } from '@/utils/format'

describe('formatGs', () => {
  it('uses dots for thousands', () => {
    expect(formatGs(35000)).toBe('Gs. 35.000')
    expect(formatGs(140000)).toBe('Gs. 140.000')
  })

  it('handles small amounts', () => {
    expect(formatGs(500)).toBe('Gs. 500')
  })
})

describe('whatsappLink', () => {
  it('keeps only digits', () => {
    expect(whatsappLink('+595 981 123-456')).toBe('https://wa.me/595981123456')
  })

  it('adds an encoded message', () => {
    expect(whatsappLink('595981123456', '¡Hola!')).toBe(
      'https://wa.me/595981123456?text=%C2%A1Hola!'
    )
  })

  it('returns null without a number', () => {
    expect(whatsappLink('')).toBeNull()
  })
})

describe('telLink', () => {
  it('keeps the leading plus', () => {
    expect(telLink('+595 (981) 123-456')).toBe('tel:+595981123456')
  })
})
