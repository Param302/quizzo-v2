import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL
axios.defaults.withCredentials = true

export const useAuthStore = defineStore('auth', {
  state: () => {
    const token = localStorage.getItem('quizzo-token')
    const user = JSON.parse(localStorage.getItem('quizzo-user') || 'null')

    // Set axios authorization header if token exists
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }

    return {
      user,
      token,
      isAuthenticated: !!token,
      loading: false,
      error: null
    }
  },

  getters: {
    isAdmin: (state) => state.user?.role === 'admin',
    isUser: (state) => state.user?.role === 'user',
    userName: (state) => state.user?.username || '',
    userFullName: (state) => state.user?.name || '',
    userEmail: (state) => state.user?.email || ''
  },

  actions: {
    setError(error) {
      this.error = error
    },

    clearError() {
      this.error = null
    },

    setLoading(loading) {
      this.loading = loading
    },

    setAuth(user, token) {
      this.user = user
      this.token = token
      this.isAuthenticated = true
      this.error = null

      // Persist to localStorage
      localStorage.setItem('quizzo-user', JSON.stringify(user))
      localStorage.setItem('quizzo-token', token)

      // Set axios authorization header
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      }
    },

    clearAuth() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      this.error = null

      // Clear localStorage
      localStorage.removeItem('quizzo-user')
      localStorage.removeItem('quizzo-token')

      // Clear axios authorization header
      delete axios.defaults.headers.common['Authorization']
    },

    async login(credentials) {
      try {
        this.setLoading(true)
        this.clearError()

        const response = await axios.post('/auth/login', credentials)
        const { user, access_token } = response.data

        this.setAuth(user, access_token)
        return { success: true }
      } catch (error) {
        const message = error.response?.data?.message || 'Login failed'
        this.setError(message)
        return { success: false, error: message }
      } finally {
        this.setLoading(false)
      }
    },

    async register(userData) {
      try {
        this.setLoading(true)
        this.clearError()

        const response = await axios.post('/auth/register', userData)

        // Registration successful, now login with the same credentials
        const loginResult = await this.login({
          email: userData.email,
          password: userData.password
        })

        return loginResult
      } catch (error) {
        const message = error.response?.data?.message || 'Registration failed'
        this.setError(message)
        return { success: false, error: message }
      } finally {
        this.setLoading(false)
      }
    },

    async logout() {
      try {
        await axios.post('/auth/logout')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.clearAuth()
      }
    },

    async checkAuth() {
      try {
        const response = await axios.get('/auth/me')
        const { user } = response.data

        this.setAuth(user, this.token)
        return true
      } catch (error) {
        this.clearAuth()
        return false
      }
    },

    async refreshToken() {
      try {
        const response = await axios.post('/auth/refresh')
        const { token } = response.data

        this.token = token
        localStorage.setItem('quizzo-token', token)
        if (token) {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        }
        return true
      } catch (error) {
        this.clearAuth()
        return false
      }
    }
  }
})
