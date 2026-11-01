import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import { autoAnimatePlugin } from '@formkit/auto-animate/vue'

import 'primeicons/primeicons.css'
import '@/assets/styles/main.css'

import router from '@/router'
import App from '@/App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(autoAnimatePlugin)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.app-dark',
    },
  },
})
app.use(ToastService)
app.use(ConfirmationService)

app.mount('#app')

// When Vue app and router are fully initialized, notify native desktop host
router.isReady().then(() => {
  /**
   * Dispatches a readiness signal to the PyWebView desktop host to close splash and reveal the window.
   */
  function notifyReady(): boolean {
    if (typeof window !== 'undefined' && (window as any).pywebview?.api?.notify_main_ready) {
      try {
        (window as any).pywebview.api.notify_main_ready()
        return true
      } catch {
        return false
      }
    }
    return false
  }

  if (!notifyReady()) {
    if (typeof window !== 'undefined') {
      window.addEventListener('pywebviewready', notifyReady)
      const interval = setInterval(() => {
        if (notifyReady()) {
          clearInterval(interval)
        }
      }, 200)
      setTimeout(() => clearInterval(interval), 3000)
    }
  }
})
