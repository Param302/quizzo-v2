<template>
    <div class="landing-page">
        <section class="hero py-5 position-relative overflow-hidden bg-blur">
            <div class="container">
                <div class="row align-items-center min-vh-75">
                    <div class="col-lg-6 animate-slide-in-left">
                        <div class="hero-content">
                            <h1 class="display-3 fw-bold mb-4 hero-title">
                                Test Your Knowledge with
                                <span class="text-gradient hero-title-highlight">Quizzo</span>
                            </h1>
                            <p class="lead mb-4 text-secondary fw-medium">
                                Join thousands of learners taking interactive quizzes across multiple categories.
                                Challenge yourself, track your progress, and compete with friends.
                            </p>
                            <div class="d-flex gap-3 flex-wrap mb-4">
                                <router-link :to="'/courses'"
                                    class="btn btn-primary btn-lg animate-bounce-in modern-btn">
                                    <i class="bi bi-play-circle me-2"></i>
                                    Explore Quizzes
                                </router-link>
                                <router-link v-if="!authStore.isAuthenticated" to="/register"
                                    class="btn btn-outline-primary btn-lg animate-bounce-in modern-btn">
                                    <i class="bi bi-person-plus me-2"></i>
                                    Sign Up
                                </router-link>
                            </div>
                            <div class="hero-features d-flex gap-3 flex-wrap">
                                <div class="feature-chip">
                                    <i class="bi bi-bell me-2"></i>
                                    <span>Daily Reminders</span>
                                </div>
                                <div class="feature-chip">
                                    <i class="bi bi-award me-2"></i>
                                    <span>Instant Certification</span>
                                </div>
                                <div class="feature-chip">
                                    <i class="bi bi-speedometer2 me-2"></i>
                                    <span>Interactive Dashboard</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6 text-center animate-slide-in-right">
                        <div class="hero-visual">
                            <div class="floating-cards cascade-cards mx-auto">
                                <div class="simple-card card-pos-1">
                                    <div class="card glass-card h-100">
                                        <div class="card-body text-center hero-card-content">
                                            <i class="bi bi-code-slash hero-card-icon text-gradient mb-3"></i>
                                            <h4 class="mb-2 hero-card-title">JavaScript</h4>
                                            <div class="hero-card-questions">25 Questions</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="simple-card card-pos-2">
                                    <div class="card glass-card h-100">
                                        <div class="card-body text-center hero-card-content">
                                            <i class="bi bi-palette hero-card-icon text-gradient mb-3"></i>
                                            <h4 class="mb-2 hero-card-title">Design</h4>
                                            <div class="hero-card-questions">20 Questions</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="simple-card card-pos-3">
                                    <div class="card glass-card h-100">
                                        <div class="card-body text-center hero-card-content">
                                            <i class="bi bi-database hero-card-icon text-gradient mb-3"></i>
                                            <h4 class="mb-2 hero-card-title">SQL</h4>
                                            <div class="hero-card-questions">30 Questions</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="hero-bg-elements">
                <div class="bg-circle circle-1"></div>
                <div class="bg-circle circle-2"></div>
            </div>
        </section>

        <section class="features py-5 bg-blur">
            <div class="container">
                <div class="col-lg-8 mx-auto text-center mb-5 animate-fade-in">
                    <h2 class="display-5 fw-bold mb-3">Why Choose Quizzo?</h2>
                    <p class="lead fw-medium">
                        Experience the next generation of online learning with our feature-rich quiz platform.
                    </p>
                </div>
                <div class="row g-4">
                    <div class="col-lg-4 col-md-6 animate-slide-up" style="animation-delay: 0.1s;">
                        <div class="feature-card text-center h-100">
                            <div class="feature-icon mx-auto">
                                <i class="bi bi-lightning-charge fs-1 text-gradient"></i>
                            </div>
                            <h4 class="fw-semibold mb-3">Instant Results</h4>
                            <p class="text-muted">
                                Get immediate feedback on your performance with detailed explanations and personalized
                                insights.
                            </p>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-6 animate-slide-up" style="animation-delay: 0.2s;">
                        <div class="feature-card text-center h-100">
                            <div class="feature-icon mx-auto">
                                <i class="bi bi-graph-up fs-1 text-gradient"></i>
                            </div>
                            <h4 class="fw-semibold mb-3">Track Progress</h4>
                            <p class="text-muted">
                                Monitor your learning journey with comprehensive analytics, progress tracking, and
                                performance insights.
                            </p>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-6 animate-slide-up" style="animation-delay: 0.3s;">
                        <div class="feature-card text-center h-100">
                            <div class="feature-icon mx-auto">
                                <i class="bi bi-award fs-1 text-gradient"></i>
                            </div>
                            <h4 class="fw-semibold mb-3">Instant Certification</h4>
                            <p class="text-muted">
                                Earn certificates instantly upon quiz completion. Download and share your achievements
                                with employers.
                            </p>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-6 animate-slide-up" style="animation-delay: 0.4s;">
                        <div class="feature-card text-center h-100">
                            <div class="feature-icon mx-auto">
                                <i class="bi bi-bell fs-1 text-gradient"></i>
                            </div>
                            <h4 class="fw-semibold mb-3">Daily Reminders</h4>
                            <p class="text-muted">
                                Stay consistent with personalized daily reminders and learning streaks to maintain your
                                progress.
                            </p>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-6 animate-slide-up" style="animation-delay: 0.5s;">
                        <div class="feature-card text-center h-100">
                            <div class="feature-icon mx-auto">
                                <i class="bi bi-collection fs-1 text-gradient"></i>
                            </div>
                            <h4 class="fw-semibold mb-3">Variety of Courses</h4>
                            <p class="text-muted">
                                Access diverse subjects from programming to design, with new courses and topics added
                                regularly.
                            </p>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-6 animate-slide-up" style="animation-delay: 0.6s;">
                        <div class="feature-card text-center h-100">
                            <div class="feature-icon mx-auto">
                                <i class="bi bi-envelope-paper fs-1 text-gradient"></i>
                            </div>
                            <h4 class="fw-semibold mb-3">Timely Reports</h4>
                            <p class="text-muted">
                                Receive a detailed monthly report of your quiz activity and progress directly in your
                                email inbox.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="cta-section">
            <div class="container text-center animate-fade-in">
                <div class="row justify-content-center">
                    <div class="col-lg-8 d-flex flex-column align-items-center gap-3">
                        <h2 class="display-5 fw-bold mb-3 cta-title">Ready to Start Your Learning Journey?</h2>
                        <p class="lead fw-medium fst-italic mb-4 cta-lead">
                            Join our community of learners and unlock your potential with interactive quizzes and
                            personalized learning paths.
                        </p>
                        <div class="d-flex gap-3 justify-content-center flex-wrap w-100">
                            <router-link v-if="!authStore.isAuthenticated" to="/register"
                                class="btn btn-light btn-lg modern-btn w-fit w-md-auto">
                                <i class="bi bi-arrow-right-circle me-2"></i>
                                Create an Account
                            </router-link>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
</script>

<style scoped>
.landing-page {
    overflow-x: hidden;
}

.min-vh-75 {
    min-height: 75vh;
}

.bg-blur {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

.hero-title {
    font-size: 3.5rem;
    line-height: 0.8;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hero-title-highlight {
    font-size: 5rem;
}

.hero-bg-elements {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 0;
    pointer-events: none;
}

.bg-circle {
    position: absolute;
    border-radius: 50%;
    filter: blur(32px);
    background: radial-gradient(circle, rgba(245, 124, 0, 0.18) 0%, transparent 80%);
    animation: float 10s ease-in-out infinite;
}

.circle-1 {
    width: 900px;
    height: 900px;
    top: -350px;
    left: -350px;
    animation-delay: 0s;
}

.circle-2 {
    width: 400px;
    height: 400px;
    top: 60%;
    left: 60%;
    background: radial-gradient(circle, rgba(245, 124, 0, 0.10) 0%, transparent 80%);
    animation-delay: 2s;
}

.modern-btn {
    border-radius: 50px;
    padding: 12px 32px;
    font-weight: 600;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.3);
}

.modern-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 124, 0, 0.4);
}

.modern-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
}

.modern-btn:hover::before {
    left: 100%;
}

.feature-chip {
    display: inline-flex;
    align-items: center;
    padding: 8px 16px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 25px;
    border: 1px solid rgba(245, 124, 0, 0.2);
    color: var(--primary, #f57c00);
    font-weight: 500;
    font-size: 0.9rem;
    transition: all 0.3s ease;
}

.feature-chip:hover {
    background: rgba(245, 124, 0, 0.1);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245, 124, 0, 0.2);
}

.hero-visual {
    position: relative;
    padding: 2rem;
    z-index: 1;
}

.floating-cards.cascade-cards {
    position: relative;
    width: 420px;
    height: 420px;
}

.simple-card {
    position: absolute;
    width: 80%;
    height: 80%;
    transition: box-shadow 0.3s, transform 0.3s, z-index 0.2s;
}

.simple-card:hover {
    z-index: 10;
}

.card-pos-1 {
    top: 0;
    left: 0;
    z-index: 3;
}

.card-pos-2 {
    top: 40px;
    left: 40px;
    z-index: 2;
}

.card-pos-3 {
    top: 80px;
    left: 80px;
    z-index: 1;
}

.glass-card {
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 32px rgba(245, 124, 0, 0.10);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    transform: translateY(-5px) scale(1.04);
    box-shadow: 0 0 32px 8px rgba(245, 124, 0, 0.18);
}

.hero-card-content {
    padding: 2.5rem 1.5rem 2rem 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
}

.hero-card-icon {
    font-size: 4.5rem;
    line-height: 1;
}

.hero-card-title {
    font-size: 1.5rem;
    letter-spacing: -1px;
}

.hero-card-questions {
    font-size: 1.25rem;
    color: #b26a00;
    margin-top: 0.5rem;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-15px);
    }
}

.features .row.g-4 {
    row-gap: 1rem;
}

.feature-card {
    padding: 2.5rem 2rem;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    position: relative;
    overflow: hidden;
    box-shadow: none;
    border: 1px solid rgba(245, 124, 0, 0.35);
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary, #f57c00), var(--primary-dark, #b26a00));
    transform: scaleX(0);
    transition: transform 0.3s ease;
    border-top-left-radius: 24px;
    border-top-right-radius: 24px;
}

.feature-card:hover::before {
    transform: scaleX(1);
}

.feature-card:hover {
    transform: translateY(-10px);
    border-color: rgba(245, 123, 0, 0.548);
}

.feature-icon {
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(245, 124, 0, 0.1);
    border-radius: 20px;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}

.feature-card:hover .feature-icon {
    background: rgba(245, 124, 0, 0.2);
    transform: scale(1.1);
}

.cta-section {
    background: linear-gradient(180deg, #fff 0%, #fffbe6 30%, #fdc792 100%);
    position: relative;
    overflow: hidden;
    padding: 6rem 0;
}

.cta-section::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    animation: float 8s ease-in-out infinite;
}

.cta-section .container {
    position: relative;
    z-index: 1;
}

.cta-title {
    color: #f57c00;
}

.cta-lead {
    color: #f57c00;
}

@media (max-width: 1200px) {
    .floating-cards.cascade-cards {
        width: 340px;
        height: 340px;
    }

    .circle-1 {
        width: 600px;
        height: 600px;
        top: -200px;
        left: -200px;
    }

    .circle-2 {
        width: 250px;
        height: 250px;
        top: 60%;
        left: 60%;
    }
}

@media (max-width: 992px) {
    .hero-title {
        font-size: 2.2rem;
    }

    .hero-title-highlight {
        font-size: 3rem;
    }

    .floating-cards.cascade-cards {
        width: 220px;
        height: 220px;
    }

    .feature-card {
        padding: 2rem 1.5rem;
    }

    .circle-1 {
        width: 350px;
        height: 350px;
        top: -100px;
        left: -100px;
    }

    .circle-2 {
        width: 120px;
        height: 120px;
        top: 70%;
        left: 60%;
    }
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 1.5rem;
        text-align: center;
    }

    .hero-title-highlight {
        font-size: 2rem;
    }

    .hero-content {
        text-align: center;
    }

    .hero-content>* {
        margin-bottom: 2.5rem;
    }

    .hero-content>*:last-child {
        margin-bottom: 0;
    }

    .floating-cards.cascade-cards {
        width: 120px;
        height: 120px;
    }

    .feature-chip {
        font-size: 0.8rem;
        padding: 6px 12px;
    }

    .circle-1 {
        width: 120px;
        height: 120px;
        top: -40px;
        left: -40px;
    }

    .circle-2 {
        width: 60px;
        height: 60px;
        top: 80%;
        left: 60%;
    }
}

@media (max-width: 576px) {
    .hero-title {
        font-size: 2rem;
    }

    .hero-title-highlight {
        font-size: 1.5rem;
    }

    .floating-cards.cascade-cards {
        width: 100px;
        height: 100px;
    }

    .feature-card {
        padding: 1.5rem;
    }

    .modern-btn {
        width: 100%;
        margin: 0.5rem 0;
    }
}
</style>
