// frontend/src/components/ui/index.tsx
// Common UI components for the Pokemon TCG AI Education Platform

import React from 'react';

// ===========================================
// LOADING & STATUS COMPONENTS
// ===========================================

export const Spinner: React.FC<{
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'red' | 'yellow';
}> = ({ size = 'md', color = 'blue' }) => {
  const sizeClasses = {
    sm: 'h-3 w-3 border',
    md: 'h-4 w-4 border-2', 
    lg: 'h-6 w-6 border-2'
  };
  
  const colorClasses = {
    blue: 'border-blue-600 border-t-transparent',
    green: 'border-green-600 border-t-transparent',
    red: 'border-red-600 border-t-transparent', 
    yellow: 'border-yellow-600 border-t-transparent'
  };

  return (
    <div className={`animate-spin rounded-full ${sizeClasses[size]} ${colorClasses[color]}`} />
  );
};

export const StatusText: React.FC<{
  children: React.ReactNode;
  variant?: 'thinking' | 'decided' | 'error' | 'success';
}> = ({ children, variant = 'thinking' }) => {
  const variantClasses = {
    thinking: 'text-blue-700',
    decided: 'text-blue-800 font-medium',
    error: 'text-red-700',
    success: 'text-green-700 font-medium'
  };

  return (
    <span className={variantClasses[variant]}>
      {children}
    </span>
  );
};

// ===========================================
// BUTTON COMPONENTS
// ===========================================

export const Button: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'pokemon' | 'ai';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}> = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'md', 
  disabled = false,
  loading = false,
  className = ''
}) => {
  const baseClasses = 'font-medium rounded-lg transition-all duration-200 flex items-center justify-center gap-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    pokemon: 'bg-gradient-to-r from-red-500 to-blue-500 hover:from-red-600 hover:to-blue-600 text-white shadow-lg',
    ai: 'bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white shadow-lg'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };
  
  const disabledClasses = disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClasses} ${className}`}
    >
      {loading && <Spinner size="sm" color="blue" />}
      {children}
    </button>
  );
};

// ===========================================
// CARD COMPONENTS
// ===========================================

export const Card: React.FC<{
  children: React.ReactNode;
  variant?: 'default' | 'pokemon' | 'ai' | 'child' | 'game';
  hover?: boolean;
  active?: boolean;
  className?: string;
  onClick?: () => void;
}> = ({ children, variant = 'default', hover = false, active = false, className = '', onClick }) => {
  const baseClasses = 'rounded-lg border-2 transition-all duration-200';
  
  const variantClasses = {
    default: 'bg-white border-gray-300',
    pokemon: 'bg-gradient-to-br from-red-50 to-blue-50 border-purple-300',
    ai: 'bg-blue-50 border-blue-300',
    child: 'bg-red-50 border-red-300',
    game: 'bg-gradient-to-br from-purple-50 to-blue-50 border-purple-300'
  };
  
  const hoverClasses = hover ? 'hover:shadow-lg hover:-translate-y-1 cursor-pointer' : '';
  const activeClasses = active ? 'border-yellow-500 bg-yellow-50 shadow-md' : '';
  const clickableClasses = onClick ? 'cursor-pointer' : '';

  return (
    <div 
      className={`${baseClasses} ${variantClasses[variant]} ${hoverClasses} ${activeClasses} ${clickableClasses} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

// ===========================================
// POKEMON TYPE COMPONENTS
// ===========================================

export const TypeBadge: React.FC<{
  type: string;
  size?: 'sm' | 'md' | 'lg';
}> = ({ type, size = 'md' }) => {
  const typeColors: Record<string, string> = {
    fire: 'bg-red-500 text-white',
    water: 'bg-blue-500 text-white', 
    grass: 'bg-green-500 text-white',
    electric: 'bg-yellow-500 text-black',
    psychic: 'bg-purple-500 text-white',
    fighting: 'bg-red-700 text-white',
    poison: 'bg-purple-700 text-white',
    ground: 'bg-yellow-700 text-white',
    rock: 'bg-yellow-800 text-white',
    bug: 'bg-green-700 text-white',
    ghost: 'bg-purple-800 text-white',
    steel: 'bg-gray-500 text-white',
    ice: 'bg-blue-300 text-black',
    dragon: 'bg-indigo-600 text-white',
    dark: 'bg-gray-800 text-white',
    fairy: 'bg-pink-500 text-white',
    normal: 'bg-gray-400 text-white',
    flying: 'bg-blue-400 text-white'
  };
  
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  const colorClass = typeColors[type.toLowerCase()] || typeColors['normal'];

  return (
    <span className={`rounded-full font-medium ${colorClass} ${sizeClasses[size]}`}>
      {type}
    </span>
  );
};

// ===========================================
// LAYOUT COMPONENTS
// ===========================================

export const Section: React.FC<{
  children: React.ReactNode;
  title?: string;
  variant?: 'default' | 'ai' | 'child' | 'game';
  className?: string;
}> = ({ children, title, variant = 'default', className = '' }) => {
  const variantClasses = {
    default: 'bg-white border-gray-300',
    ai: 'bg-blue-50 border-blue-300',
    child: 'bg-red-50 border-red-300', 
    game: 'bg-gradient-to-br from-purple-50 to-blue-50 border-purple-300'
  };
  
  const titleColors = {
    default: 'text-gray-800',
    ai: 'text-blue-800',
    child: 'text-red-800',
    game: 'text-purple-800'
  };

  return (
    <div className={`border-2 rounded-lg p-4 ${variantClasses[variant]} ${className}`}>
      {title && (
        <h3 className={`font-bold mb-3 ${titleColors[variant]}`}>
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};

export const Grid: React.FC<{
  children: React.ReactNode;
  cols?: 1 | 2 | 3 | 4;
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ children, cols = 2, gap = 'md', className = '' }) => {
  const colClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 lg:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  };
  
  const gapClasses = {
    sm: 'gap-2',
    md: 'gap-4', 
    lg: 'gap-6'
  };

  return (
    <div className={`grid ${colClasses[cols]} ${gapClasses[gap]} ${className}`}>
      {children}
    </div>
  );
};

// ===========================================
// EDUCATIONAL COMPONENTS
// ===========================================

export const LessonBox: React.FC<{
  children: React.ReactNode;
  type?: 'tip' | 'lesson' | 'strategy' | 'warning';
  icon?: string;
}> = ({ children, type = 'lesson', icon }) => {
  const typeStyles = {
    tip: 'bg-green-100 border-green-300 text-green-800',
    lesson: 'bg-blue-100 border-blue-300 text-blue-800', 
    strategy: 'bg-purple-100 border-purple-300 text-purple-800',
    warning: 'bg-yellow-100 border-yellow-300 text-yellow-800'
  };
  
  const defaultIcons = {
    tip: '💡',
    lesson: '🎓',
    strategy: '🎯', 
    warning: '⚠️'
  };

  const displayIcon = icon || defaultIcons[type];

  return (
    <div className={`border-2 rounded-lg p-3 ${typeStyles[type]}`}>
      <div className="flex items-start gap-2">
        <span className="text-lg flex-shrink-0">{displayIcon}</span>
        <div className="text-sm">{children}</div>
      </div>
    </div>
  );
};

export const ProgressBar: React.FC<{
  value: number;
  max: number;
  label?: string;
  color?: 'blue' | 'green' | 'red' | 'yellow';
}> = ({ value, max, label, color = 'blue' }) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  const colorClasses = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    red: 'bg-red-600',
    yellow: 'bg-yellow-600'
  };

  return (
    <div className="w-full">
      {label && <div className="text-sm font-medium text-gray-700 mb-1">{label}</div>}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${colorClasses[color]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="text-xs text-gray-600 mt-1">{value} / {max}</div>
    </div>
  );
};