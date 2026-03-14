import { forwardRef } from 'react'

const InputField = forwardRef(function InputField(
  { id, label, type = 'text', placeholder, error, rightElement, ...props },
  ref
) {
  return (
    <div className="flex flex-col gap-1.5">
      <label
        htmlFor={id}
        className="text-sm font-600 text-gray-700"
        style={{ fontSize: '0.95rem', fontWeight: 600 }}
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
            'w-full px-4 py-3.5 rounded-xl border-2 text-base bg-white outline-none',
            'placeholder-gray-400 text-gray-800',
            'focus:border-[#1d348a] focus:ring-3 focus:ring-[#c2d1e7]',
            error
              ? 'border-[#EF4444] bg-red-50'
              : 'border-[#c2d1e7] hover:border-[#1d348a]/50',
            rightElement ? 'pr-12' : '',
          ]
            .filter(Boolean)
            .join(' ')}
          style={{ fontSize: '1rem', lineHeight: '1.6' }}
          {...props}
        />
        {rightElement && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {rightElement}
          </div>
        )}
      </div>
      {error && (
        <p
          id={`${id}-error`}
          role="alert"
          className="text-sm flex items-center gap-1.5"
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
