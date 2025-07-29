<template>
    <nav class="navbar navbar-expand-lg fixed-top bg-transparent border-bottom modern-navbar">
        <div class="container">
            <!-- Brand with Animation -->
            <router-link to="/" class="navbar-brand fw-bold fs-2 animated-brand">
                <span class="brand-text">Quizzo</span>
            </router-link>

            <!-- Mobile toggle -->
            <button
                class="navbar-toggler custom-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarNav"
                aria-controls="navbarNav"
                aria-expanded="false"
                aria-label="Toggle navigation"
            >
                <span></span>
                <span></span>
                <span></span>
            </button>

            <!-- Navigation -->
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-lg-center">
                    <li class="nav-item me-2" v-if="!authStore.isAuthenticated">
                        <router-link
                            to="/register"
                            class="btn btn-outline-secondary rounded-pill px-4"
                        >
                            Sign Up
                        </router-link>
                    </li>
                    <li class="nav-item" v-if="!authStore.isAuthenticated">
                        <router-link
                            to="/login"
                            class="btn btn-primary rounded-pill px-4"
                        >
                            Dashboard
                        </router-link>
                    </li>
                    <li class="nav-item" v-else>
                        <router-link
                            to="/dashboard"
                            class="btn btn-primary rounded-pill px-4"
                        >
                            Dashboard
                        </router-link>
                    </li>

                    <!-- Authenticated user avatar (desktop) -->
                    <li
                        v-if="authStore.isAuthenticated"
                        class="nav-item dropdown d-none d-lg-block ms-3"
                    >
                        <a
                            class="nav-link dropdown-toggle user-avatar"
                            href="#"
                            role="button"
                            data-bs-toggle="dropdown"
                        >
                            <div class="avatar-circle">
                                {{ userInitials }}
                            </div>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li>
                                <router-link
                                    :to="`/u/@${authStore.user?.username || ''}`"
                                    class="dropdown-item"
                                >
                                    <i class="bi bi-person me-2"></i>
                                    Profile
                                </router-link>
                            </li>
                            <li v-if="authStore.isAdmin">
                                <hr class="dropdown-divider" />
                            </li>
                            <li v-if="authStore.isAdmin">
                                <router-link to="/admin" class="dropdown-item">
                                    <i class="bi bi-speedometer2 me-2"></i>
                                    Admin Panel
                                </router-link>
                            </li>
                            <li>
                                <hr class="dropdown-divider" />
                            </li>
                            <li>
                                <button
                                    @click="handleLogout"
                                    class="dropdown-item text-danger"
                                    type="button"
                                >
                                    <i class="bi bi-box-arrow-right me-2"></i>
                                    Logout
                                </button>
                            </li>
                        </ul>
                    </li>

                    <!-- Mobile user menu -->
                    <li
                        v-if="authStore.isAuthenticated"
                        class="nav-item d-lg-none w-100"
                    >
                        <div class="mobile-user-info">
                            <div class="d-flex align-items-center mb-2">
                                <div class="avatar-circle me-2">
                                    {{ userInitials }}
                                </div>
                                <span class="text-white">{{ authStore.userName }}</span>
                            </div>
                            <div class="mobile-menu-items">
                                <router-link
                                    :to="`/u/@${authStore.user?.username || ''}`"
                                    class="mobile-menu-item"
                                >
                                    <i class="bi bi-person me-2"></i>
                                    Profile
                                </router-link>
                                <router-link
                                    v-if="authStore.isAdmin"
                                    to="/admin"
                                    class="mobile-menu-item"
                                >
                                    <i class="bi bi-speedometer2 me-2"></i>
                                    Admin Panel
                                </router-link>
                                <button
                                    @click="handleLogout"
                                    class="mobile-menu-item text-danger border-0 bg-transparent"
                                    type="button"
                                >
                                    <i class="bi bi-box-arrow-right me-2"></i>
                                    Logout
                                </button>
                            </div>
                        </div>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const userInitials = computed(() => {
    const name = authStore.userName
    if (!name) return 'U'
    const parts = name.split(' ')
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return name[0].toUpperCase()
})

const handleLogout = async () => {
    await authStore.logout()
    router.push('/')
}

// Handle navbar scroll effect
const handleScroll = () => {
    const navbarElement = document.querySelector('.modern-navbar')
    if (navbarElement) {
        if (window.scrollY > 50) {
            navbarElement.classList.add('scrolled')
        } else {
            navbarElement.classList.remove('scrolled')
        }
    }
}

onMounted(() => {
    window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* Modern Transparent Navbar */
.modern-navbar {
    background-color: transparent;
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1rem 0;
    transition: background-color 0.3s, box-shadow 0.3s;
    z-index: 1050;
}

.modern-navbar.scrolled {
    background-color: rgba(255, 255, 255, 0.95);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

/* Animated Brand */
.animated-brand {
    color: var(--primary);
    transition: color 0.3s, transform 0.3s;
    text-shadow: none;
    text-decoration: none;
}

.animated-brand:hover {
    color: var(--primary-dark);
    transform: scale(1.02);
}

.brand-text {
    position: relative;
    display: inline-block;
}

/* Custom Toggler */
.custom-toggler {
    border: none;
    padding: 4px 8px;
    background: transparent;
    width: 30px;
    height: 24px;
    box-shadow: none;
}

.custom-toggler span {
    display: block;
    width: 22px;
    height: 2px;
    background: var(--primary);
    margin: 4px 0;
    transition: transform 0.3s, opacity 0.3s;
    border-radius: 2px;
}

.custom-toggler:not(.collapsed) span:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
}

.custom-toggler:not(.collapsed) span:nth-child(2) {
    opacity: 0;
}

.custom-toggler:not(.collapsed) span:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -6px);
}

/* Button Styles */
.btn-outline-secondary {
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: rgba(255, 255, 255, 0.9);
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    font-weight: 600;
    transition: background 0.3s, color 0.3s, border-color 0.3s, box-shadow 0.3s, transform 0.3s;
    position: relative;
    overflow: hidden;
}

.btn-outline-secondary:hover {
    border-color: rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.2);
    color: #fff;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border: none;
    font-weight: 600;
    transition: background 0.3s, box-shadow 0.3s, transform 0.3s;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.btn-primary:hover {
    background: linear-gradient(135deg, var(--primary-dark) 0%, #d84315 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
}

.btn-primary::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
    pointer-events: none;
}

.btn-primary:hover::before {
    left: 100%;
}

/* Avatar Styles */
.user-avatar {
    text-decoration: none;
    transition: color 0.3s;
}

.avatar-circle {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: 600;
    font-size: 14px;
    box-shadow: 0 2px 10px rgba(245, 124, 0, 0.3);
    transition: transform 0.3s, box-shadow 0.3s;
}

.user-avatar:hover .avatar-circle {
    transform: scale(1.1);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.4);
}

/* Dropdown Styles */
.dropdown-menu {
    border: none;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    margin-top: 0.5rem;
    padding: 0.5rem 0;
}

.dropdown-item {
    color: var(--text-primary);
    padding: 0.75rem 1.5rem;
    transition: background 0.3s, color 0.3s, transform 0.3s;
    border-radius: 8px;
    margin: 0 0.5rem;
}

.dropdown-item:hover {
    background: linear-gradient(135deg, var(--primary-50) 0%, rgba(245, 124, 0, 0.1) 100%);
    color: var(--primary);
    transform: translateX(5px);
}

/* Mobile Styles */
.mobile-user-info {
    padding: 1rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
}

.mobile-menu-items {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.mobile-menu-item {
    color: rgba(255, 255, 255, 0.9);
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: background 0.3s, color 0.3s, transform 0.3s;
    display: flex;
    align-items: center;
    width: 100%;
    text-align: left;
}

.mobile-menu-item:hover {
    background: rgba(255, 255, 255, 0.2);
    color: #fff;
    transform: translateX(5px);
}

/* Responsive Design */
@media (max-width: 991.98px) {
    .navbar-collapse {
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(20px);
        border-radius: 12px;
        margin-top: 1rem;
        padding: 1.5rem;
    }

    .animated-brand {
        font-size: 1.75rem;
    }

    .btn-outline-secondary,
    .btn-primary {
        width: 100%;
        margin: 0.25rem 0;
    }
}

@media (max-width: 575.98px) {
    .animated-brand {
        font-size: 1.5rem;
    }

    .modern-navbar {
        padding: 0.75rem 0;
    }
}

/* Add top padding to body to account for fixed navbar */
:global(body) {
    padding-top: 80px;
}

@media (max-width: 575.98px) {
    :global(body) {
        padding-top: 70px;
    }
}
</style>