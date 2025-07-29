import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

// Add Bootstrap Icons CDN link to head
if (!document.querySelector('link[href*="bootstrap-icons"]')) {
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css'
    document.head.appendChild(link)
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
