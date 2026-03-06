@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ─── ZOARIA Design Tokens ─────────────────────────────────────────────── */
:root {
  --brand-primary:    #14b8a6;
  --brand-secondary:  #0d9488;
  --bg-base:          #fdfcf8;
  --bg-subtle:        #f4f9f4;
  --bg-card:          #ffffff;
  --text-primary:     #111818;
  --text-secondary:   #546161;
  --text-muted:       #9aa3a3;
  --border:           #e5f2e5;
  --border-strong:    #cce5cc;
  --shadow-card:      0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  --radius-card:      16px;
}

[data-theme="dark"] {
  --bg-base:        #080e0e;
  --bg-subtle:      #111818;
  --bg-card:        #1e2828;
  --text-primary:   #f4f9f4;
  --text-secondary: #9aa3a3;
  --text-muted:     #6f7c7c;
  --border:         #303b3b;
  --border-strong:  #404d4d;
}

/* ─── Base Resets ────────────────────────────────────────────────────────── */
* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: 'DM Sans', sans-serif;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

/* ─── Typography ─────────────────────────────────────────────────────────── */
h1, h2, h3 {
  font-family: 'Playfair Display', serif;
  line-height: 1.2;
}

h4, h5, h6 {
  font-family: 'DM Sans', sans-serif;
  font-weight: 600;
}

/* ─── Utility Classes ────────────────────────────────────────────────────── */
@layer components {
  .zoaria-card {
    @apply bg-white rounded-3xl shadow-card border border-sage-100 p-6 transition-shadow duration-200;
  }

  .zoaria-card:hover {
    @apply shadow-card-hover;
  }

  .btn-primary {
    @apply bg-brand-500 hover:bg-brand-600 text-white font-semibold px-6 py-3 rounded-2xl
           transition-all duration-200 active:scale-[0.97] shadow-sm hover:shadow-glow
           disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none;
  }

  .btn-secondary {
    @apply bg-sage-50 hover:bg-sage-100 text-sage-700 font-semibold px-6 py-3 rounded-2xl
           border border-sage-200 transition-all duration-200 active:scale-[0.97];
  }

  .btn-ghost {
    @apply text-sage-600 hover:text-brand-600 hover:bg-brand-50 font-medium px-4 py-2 rounded-xl
           transition-all duration-150;
  }

  .input-base {
    @apply w-full px-4 py-3 rounded-2xl border border-sage-200 bg-white text-obsidian-800
           placeholder-obsidian-300 focus:outline-none focus:ring-2 focus:ring-brand-400
           focus:border-brand-400 transition-all duration-150 font-body text-sm;
  }

  .label-base {
    @apply block text-sm font-semibold text-obsidian-600 mb-1.5;
  }

  .badge {
    @apply inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold;
  }

  .nav-link {
    @apply flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium
           text-obsidian-500 hover:text-brand-600 hover:bg-brand-50
           transition-all duration-150;
  }

  .nav-link.active {
    @apply bg-brand-50 text-brand-700 font-semibold;
  }

  /* Skeleton loader */
  .skeleton {
    @apply bg-gradient-to-r from-sage-100 via-sage-50 to-sage-100 animate-shimmer;
    background-size: 200% 100%;
  }

  /* Status indicators */
  .status-healthy    { @apply text-status-healthy bg-green-50 border-green-200; }
  .status-overweight { @apply text-status-overweight bg-amber-50 border-amber-200; }
  .status-underweight{ @apply text-status-underweight bg-red-50 border-red-200; }
}

/* ─── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cce5cc; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #99c299; }

/* ─── Selection ──────────────────────────────────────────────────────────── */
::selection { background: rgba(20,184,166,0.2); color: inherit; }

/* ─── Page Transition Wrapper ─────────────────────────────────────────────── */
.page-enter {
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
