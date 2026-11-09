export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-900 via-primary-700 to-primary-500 p-4 relative overflow-hidden">
      {/* Decorative circles */}
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
      <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl" />
      <div className="absolute top-1/3 right-1/4 w-64 h-64 bg-primary-300/10 rounded-full blur-2xl" />

      {/* Brand mark */}
      <div className="absolute top-6 left-6 flex items-center gap-2">
        <div className="w-9 h-9 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
          <span className="text-white font-black text-xl">W</span>
        </div>
        <span className="text-white font-bold text-lg tracking-tight">WorkBuddy</span>
      </div>

      {/* Card */}
      <div className="relative w-full max-w-md animate-slide-up">
        <div className="bg-white dark:bg-surface-900 rounded-3xl shadow-2xl overflow-hidden">
          {children}
        </div>
      </div>
    </div>
  )
}
