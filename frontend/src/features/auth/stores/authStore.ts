import { defineStore } from 'pinia'
import { ref } from 'vue'
import { nativeBridge } from '@/services/nativeBridge'
import type { AuthUser } from '@/types/generated/AuthUser'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(false)
  const currentUser = ref<AuthUser | null>(null)
  const isInitialized = ref(false)

  async function checkAuthStatus() {
    if (isLoggedIn.value) {
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
    currentUser.value = user
    isInitialized.value = true
  }

  async function logout() {
    try {
      await nativeBridge.logout()
    } catch {
      // ignore
    }
    isLoggedIn.value = false
    currentUser.value = null
  }

  return {
    isLoggedIn,
    currentUser,
    isInitialized,
    checkAuthStatus,
    setAuthenticated,
    logout,
  }
})
