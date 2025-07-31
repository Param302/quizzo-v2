import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
import GeneralLayout from '@/layouts/GeneralLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

// Pages
import LandingPage from '@/pages/LandingPage.vue'
import Courses from '@/pages/Courses.vue'
import ChapterPage from '@/pages/ChapterPage.vue'
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue'
import UserDashboard from '@/pages/UserDashboard.vue'
import Quiz from '@/pages/Quiz.vue'
import PublicProfile from '@/pages/PublicProfile.vue'
import AdminDashboard from '@/pages/AdminDashboard.vue'
import AdminUsers from '@/pages/AdminUsers.vue'
import AdminQuizzes from '@/pages/AdminQuizzes.vue'
import AdminCourses from '@/pages/AdminCourses.vue'
import AdminChapterPage from '@/pages/AdminChapterPage.vue'
import QuizSubmission from '@/pages/QuizSubmission.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: GeneralLayout,
      children: [
        {
          path: '',
          name: 'landing',
          component: LandingPage
        },
        {
          path: '/courses',
          name: 'courses',
          component: Courses
        },
        {
          path: '/course/:courseId/chapter/:chapterId',
          name: 'chapter',
          component: ChapterPage
        },
        {
          path: '/dashboard',
          name: 'dashboard',
          component: UserDashboard,
          meta: { requiresAuth: true, role: 'user' }
        },
        {
          path: '/quiz/:id',
          name: 'quiz',
          component: Quiz,
          meta: { requiresAuth: true }
        },
        {
          path: '/quiz/:quizId/submission',
          name: 'quiz-submission',
          component: QuizSubmission,
          meta: { requiresAuth: true }
        },
        {
          path: '/u/@:username',
          name: 'profile',
          component: PublicProfile
        },
        {
          path: '/admin',
          name: 'admin',
          component: AdminDashboard,
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: '/admin/manage/users',
          name: 'admin-manage-users',
          component: AdminUsers,
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: '/admin/manage/course',
          name: 'admin-manage-courses',
          component: AdminCourses,
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: '/admin/manage/course/:courseId/chapter/:chapterId',
          name: 'admin-manage-chapter',
          component: AdminChapterPage,
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: '/admin/quizzes',
          name: 'admin-quizzes',
          component: AdminQuizzes,
          meta: { requiresAuth: true, role: 'admin' }
        }
      ]
    },
    {
      path: '/auth',
      component: AuthLayout,
      children: [
        {
          path: '/login',
          name: 'login',
          component: Login,
          meta: { requiresGuest: true }
        },
        {
          path: '/register',
          name: 'register',
          component: Register,
          meta: { requiresGuest: true }
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next({ name: 'login' })
      return
    }

    // Check role-based access
    if (to.meta.role && authStore.user?.role !== to.meta.role) {
      next({ name: 'courses' })
      return
    }
  }

  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }

  next()
})

export default router
