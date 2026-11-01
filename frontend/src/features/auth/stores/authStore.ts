import { defineStore } from 'pinia'
import { ref } from 'vue'
import { nativeBridge } from '@/services/nativeBridge'
import type { AuthUser } from '@/types/generated/AuthUser'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(false)
  const isGuest = ref(false)
  const currentUser = ref<AuthUser | null>(null)
  const isInitialized = ref(false)

  async function checkAuthStatus() {
    if (isGuest.value) {
      isInitialized.value = true
      return
    }
    try {
      const status = await nativeBridge.getStatus()
      if (status.loggedIn && status.user) {
        isLoggedIn.value = true
        currentUser.value = status.user
      } else {
        isLoggedIn.value = false
        currentUser.value = null
      }
    } catch (e) {
      console.warn('Failed to check auth status:', e)
      isLoggedIn.value = false
      currentUser.value = null
    } finally {
      isInitialized.value = true
    }
  }

  function setAuthenticated(user: AuthUser) {
    isLoggedIn.value = true
    isGuest.value = false
    currentUser.value = user
    isInitialized.value = true
  }

  function setGuestMode() {
    isLoggedIn.value = true
    isGuest.value = true
    currentUser.value = {
      id: BigInt(0) as unknown as bigint,
      name: 'Khách / Chế độ Offline',
      email: 'guest@aipro.studio',
      avatar: undefined,
    }
    isInitialized.value = true
  }

  async function logout() {
    try {
      await nativeBridge.logout()
    } catch {
      // ignore
    }
    isLoggedIn.value = false
    isGuest.value = false
    currentUser.value = null
  }

  return {
    isLoggedIn,
    isGuest,
    currentUser,
    isInitialized,
    checkAuthStatus,
    setAuthenticated,
    setGuestMode,
    logout,
  }
})
