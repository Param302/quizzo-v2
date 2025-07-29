<template>
    <footer class="footer mt-auto py-4 border-top">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-6 mb-3 mb-md-0 text-center text-md-start">
                    <h3 class="footer-brand">Quizzo</h3>
                </div>
                <div class="col-md-6 text-center text-md-end">
                    <p class="mb-0 footer-credit">
                        Made with <span class="heart">🧡</span> by
                        <a
                            href="https://github.com/Param302"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="author-link"
                        >
                            Parampreet Singh
                        </a>
                    </p>
                </div>
            </div>
        </div>
    </footer>
</template>

<script setup>
</script>

<style scoped>
.footer {
    background: linear-gradient(135deg, var(--bg-subtle) 0%, white 100%);
}

.footer-brand {
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 1.8rem;
    color: var(--primary);
    margin: 0;
    transition: color 0.3s, transform 0.3s;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.footer-brand:hover {
    color: var(--primary-dark);
    transform: scale(1.02);
}

.footer-credit {
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 500;
}

.heart {
    display: inline-block;
    animation: heartbeat 2s ease-in-out infinite;
    font-size: 1.1em;
}

@keyframes heartbeat {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
}

.author-link {
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s, text-decoration 0.3s;
}

.author-link:hover {
    color: var(--primary-dark);
    text-decoration: underline;
}

@media (max-width: 767.98px) {
    .footer-brand {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .footer-credit {
        font-size: 0.9rem;
    }
}
</style>
