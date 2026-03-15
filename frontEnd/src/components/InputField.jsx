import { forwardRef } from 'react'

const InputField = forwardRef(function InputField(
  { id, label, type = 'text', placeholder, error, rightElement, ...props },
  ref
) {
  return (
    <div className="flex flex-col gap-3">
      <label
        htmlFor={id}
        className="text-xl font-bold text-gray-700 tracking-wide pl-1"
      >
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          ref={ref}
          type={type}
          placeholder={placeholder}
          aria-describedby={error ? `${id}-error` : undefined}
          aria-invalid={error ? 'true' : 'false'}
          className={[
            'w-full px-6 py-5 rounded-3xl border-[3px] text-xl bg-[#f8fafc] outline-none transition-all',
            'placeholder-gray-400 text-gray-800',
            'focus:border-[#1d348a] focus:ring-4 focus:ring-[#c2d1e7] focus:bg-white',
            error
              ? 'border-[#EF4444] bg-red-50'
              : 'border-[#e8eef6] hover:border-[#1d348a]/50 hover:bg-white',
            rightElement ? 'pr-16' : '',
          ]
            .filter(Boolean)
            .join(' ')}
          {...props}
        />
        {rightElement && (
          <div className="absolute right-5 top-1/2 -translate-y-1/2">
            {rightElement}
          </div>
        )}
      </div>
      {error && (
        <p
          id={`${id}-error`}
          role="alert"
          className="text-lg flex items-center gap-2 mt-1 font-medium"
          style={{ color: '#EF4444' }}
        >
          <span aria-hidden="true">⚠</span>
          {error}
        </p>
      )}
    </div>
  )
})

export default InputField
