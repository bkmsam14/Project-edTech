function Button({
  children,
  variant = 'primary',
  type = 'button',
  fullWidth = false,
  disabled = false,
  onClick,
  className = '',
  ...props
}) {
  const base =
    'inline-flex items-center justify-center gap-2 font-semibold rounded-xl text-base px-6 py-3.5 cursor-pointer focus:outline-none focus:ring-3 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed'

  const variants = {
    primary:
      'bg-[#1d348a] text-white hover:bg-[#162870] focus:ring-[#c2d1e7] active:scale-[0.98]',
    secondary:
      'bg-[#c2d1e7] text-[#1d348a] hover:bg-[#b0c2d8] focus:ring-[#1d348a]/30 active:scale-[0.98]',
    ghost:
      'bg-transparent text-[#1d348a] hover:bg-[#c2d1e7]/40 focus:ring-[#1d348a]/20 active:scale-[0.98]',
  }

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={[base, variants[variant], fullWidth ? 'w-full' : '', className]
        .filter(Boolean)
        .join(' ')}
      style={{ fontSize: '1rem', lineHeight: '1.5', transition: 'all 0.2s ease' }}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button
