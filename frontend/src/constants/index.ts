// frontend/src/constants/index.ts
// Centralized constants for the Pokemon TCG AI Education Platform

// ===========================================
// POKEMON TYPE SYSTEM
// ===========================================

export const POKEMON_TYPES = {
  FIRE: 'Fire',
  WATER: 'Water', 
  GRASS: 'Grass',
  ELECTRIC: 'Electric',
  PSYCHIC: 'Psychic',
  FIGHTING: 'Fighting',
  POISON: 'Poison',
  GROUND: 'Ground',
  ROCK: 'Rock',
  BUG: 'Bug',
  GHOST: 'Ghost',
  STEEL: 'Steel',
  ICE: 'Ice',
  DRAGON: 'Dragon',
  DARK: 'Dark',
  FAIRY: 'Fairy',
  NORMAL: 'Normal',
  FLYING: 'Flying'
} as const;

export type PokemonType = typeof POKEMON_TYPES[keyof typeof POKEMON_TYPES];

// Type effectiveness chart for AI education
export const TYPE_EFFECTIVENESS: Record<string, string[]> = {
  [POKEMON_TYPES.FIRE]: [POKEMON_TYPES.GRASS, POKEMON_TYPES.BUG, POKEMON_TYPES.STEEL, POKEMON_TYPES.ICE],
  [POKEMON_TYPES.WATER]: [POKEMON_TYPES.FIRE, POKEMON_TYPES.GROUND, POKEMON_TYPES.ROCK],
  [POKEMON_TYPES.GRASS]: [POKEMON_TYPES.WATER, POKEMON_TYPES.GROUND, POKEMON_TYPES.ROCK],
  [POKEMON_TYPES.ELECTRIC]: [POKEMON_TYPES.WATER, POKEMON_TYPES.FLYING],
  [POKEMON_TYPES.ICE]: [POKEMON_TYPES.GRASS, POKEMON_TYPES.GROUND, POKEMON_TYPES.FLYING, POKEMON_TYPES.DRAGON],
  [POKEMON_TYPES.FIGHTING]: [POKEMON_TYPES.NORMAL, POKEMON_TYPES.ROCK, POKEMON_TYPES.STEEL, POKEMON_TYPES.ICE, POKEMON_TYPES.DARK],
  [POKEMON_TYPES.POISON]: [POKEMON_TYPES.GRASS, POKEMON_TYPES.FAIRY],
  [POKEMON_TYPES.GROUND]: [POKEMON_TYPES.FIRE, POKEMON_TYPES.ELECTRIC, POKEMON_TYPES.POISON, POKEMON_TYPES.ROCK, POKEMON_TYPES.STEEL],
  [POKEMON_TYPES.FLYING]: [POKEMON_TYPES.GRASS, POKEMON_TYPES.FIGHTING, POKEMON_TYPES.BUG],
  [POKEMON_TYPES.PSYCHIC]: [POKEMON_TYPES.FIGHTING, POKEMON_TYPES.POISON],
  [POKEMON_TYPES.BUG]: [POKEMON_TYPES.GRASS, POKEMON_TYPES.PSYCHIC, POKEMON_TYPES.DARK],
  [POKEMON_TYPES.ROCK]: [POKEMON_TYPES.FIRE, POKEMON_TYPES.ICE, POKEMON_TYPES.FLYING, POKEMON_TYPES.BUG],
  [POKEMON_TYPES.GHOST]: [POKEMON_TYPES.PSYCHIC, POKEMON_TYPES.GHOST],
  [POKEMON_TYPES.DRAGON]: [POKEMON_TYPES.DRAGON],
  [POKEMON_TYPES.DARK]: [POKEMON_TYPES.PSYCHIC, POKEMON_TYPES.GHOST],
  [POKEMON_TYPES.STEEL]: [POKEMON_TYPES.ICE, POKEMON_TYPES.ROCK, POKEMON_TYPES.FAIRY],
  [POKEMON_TYPES.FAIRY]: [POKEMON_TYPES.FIGHTING, POKEMON_TYPES.DRAGON, POKEMON_TYPES.DARK]
};

// ===========================================
// GAME CONSTANTS
// ===========================================

export const GAME_CONFIG = {
  // Game rules
  STARTING_HAND_SIZE: 7,
  PRIZE_CARDS: 6,
  MAX_BENCH_SIZE: 5,
  
  // AI timing
  AI_THINKING_DURATION: 2000, // 2 seconds
  ANIMATION_DURATION: 300,     // 0.3 seconds
  
  // Turn phases
  TURN_PHASES: {
    DRAW: 'draw',
    MAIN: 'main', 
    ATTACK: 'attack',
    END: 'end'
  } as const,
  
  // Game phases
  GAME_PHASES: {
    SETUP: 'setup',
    PLAYING: 'playing',
    FINISHED: 'finished'
  } as const
};

// ===========================================
// UI CONSTANTS
// ===========================================

export const UI_CONFIG = {
  // Card sizes
  CARD_SIZES: {
    SM: { width: 'w-20', height: 'h-28', text: 'text-xs' },
    MD: { width: 'w-32', height: 'h-44', text: 'text-sm' },
    LG: { width: 'w-40', height: 'h-56', text: 'text-base' }
  },
  
  // Animation classes
  ANIMATIONS: {
    THINKING: 'animate-pulse',
    BOUNCE: 'animate-bounce',
    SPIN: 'animate-spin',
    POKEMON_HOVER: 'pokemon-card'
  },
  
  // Color variants
  VARIANTS: {
    DEFAULT: 'default',
    POKEMON: 'pokemon',
    AI: 'ai', 
    CHILD: 'child',
    GAME: 'game'
  }
};

// ===========================================
// AI EDUCATION CONSTANTS
// ===========================================

export const AI_EDUCATION = {
  // Learning objectives
  CONCEPTS: {
    PATTERN_RECOGNITION: 'pattern_recognition',
    STRATEGIC_THINKING: 'strategic_thinking',
    DECISION_MAKING: 'decision_making',
    LEARNING_FROM_DATA: 'learning_from_data'
  },
  
  // AI explanation types
  EXPLANATION_TYPES: {
    TYPE_ADVANTAGE: 'type_advantage',
    STRATEGIC_DECISION: 'strategic_decision',
    PATTERN_ANALYSIS: 'pattern_analysis',
    RISK_ASSESSMENT: 'risk_assessment'
  },
  
  // Educational message templates
  MESSAGES: {
    AI_THINKING: '🤖 AI is analyzing the battlefield...',
    TYPE_ADVANTAGE: '🧠 My AI remembered that {attacking} beats {defending}!',
    STRATEGIC_MOVE: '🎯 My AI calculated this is the optimal move!',
    PATTERN_RECOGNITION: '📊 My AI detected a familiar pattern from previous games!',
    LEARNING_MOMENT: '🎓 This is how AI processes information and makes decisions!'
  }
};

// ===========================================
// SAMPLE POKEMON DATA
// ===========================================

export const SAMPLE_POKEMON = [
  {
    id: 'charmander-1',
    name: 'Charmander',
    hp: 50,
    types: [POKEMON_TYPES.FIRE],
    attacks: [
      { name: 'Scratch', damage: 10, cost: ['Colorless'] },
      { name: 'Ember', damage: 30, cost: [POKEMON_TYPES.FIRE, 'Colorless'] }
    ]
  },
  {
    id: 'squirtle-1', 
    name: 'Squirtle',
    hp: 50,
    types: [POKEMON_TYPES.WATER],
    attacks: [
      { name: 'Tackle', damage: 10, cost: ['Colorless'] },
      { name: 'Water Gun', damage: 30, cost: [POKEMON_TYPES.WATER, 'Colorless'] }
    ]
  },
  {
    id: 'bulbasaur-1',
    name: 'Bulbasaur', 
    hp: 50,
    types: [POKEMON_TYPES.GRASS],
    attacks: [
      { name: 'Tackle', damage: 10, cost: ['Colorless'] },
      { name: 'Vine Whip', damage: 30, cost: [POKEMON_TYPES.GRASS, 'Colorless'] }
    ]
  },
  {
    id: 'pikachu-1',
    name: 'Pikachu',
    hp: 60,
    types: [POKEMON_TYPES.ELECTRIC],
    attacks: [
      { name: 'Thunder Shock', damage: 20, cost: [POKEMON_TYPES.ELECTRIC] },
      { name: 'Thunderbolt', damage: 40, cost: [POKEMON_TYPES.ELECTRIC, POKEMON_TYPES.ELECTRIC] }
    ]
  }
];

// ===========================================
// TYPESCRIPT TYPES
// ===========================================

export interface PokemonCard {
  id: string;
  name: string;
  hp: number;
  types: PokemonType[];
  attacks: Attack[];
  image?: string;
  stage?: 'Basic' | 'Stage 1' | 'Stage 2';
  evolvesFrom?: string;
  weaknesses?: Weakness[];
  resistances?: Resistance[];
  retreatCost?: number;
}

export interface Attack {
  name: string;
  damage: number | string;
  cost: (PokemonType | string)[];
  effect?: string;
}

export interface Weakness {
  type: PokemonType;
  multiplier: number;
}

export interface Resistance {
  type: PokemonType;
  reduction: number;
}

export interface Player {
  name: string;
  activePokemon: PokemonCard | null;
  benchedPokemon: PokemonCard[];
  hand: PokemonCard[];
  prizeCards: number;
}

export interface GameState {
  currentTurn: 'child' | 'ai';
  gamePhase: 'setup' | 'playing' | 'finished';
  childPlayer: Player;
  aiPlayer: Player;
  winner: string | null;
  turnNumber: number;
}

export interface AIThought {
  thinking: boolean;
  message: string;
  explanation: string;
  typeLesson?: string;
  strategicInsight?: string;
  concept?: keyof typeof AI_EDUCATION.CONCEPTS;
}

// ===========================================
// UTILITY FUNCTIONS
// ===========================================

export const getTypeAdvantage = (attackingType: PokemonType, defendingType: PokemonType): 'super_effective' | 'not_very_effective' | 'neutral' => {
  if (TYPE_EFFECTIVENESS[attackingType]?.includes(defendingType)) {
    return 'super_effective';
  }
  
  if (TYPE_EFFECTIVENESS[defendingType]?.includes(attackingType)) {
    return 'not_very_effective';
  }
  
  return 'neutral';
};

export const getTypeIcon = (type: PokemonType): string => {
  const typeIcons: Record<PokemonType, string> = {
    [POKEMON_TYPES.FIRE]: '🔥',
    [POKEMON_TYPES.WATER]: '💧',
    [POKEMON_TYPES.GRASS]: '🌱',
    [POKEMON_TYPES.ELECTRIC]: '⚡',
    [POKEMON_TYPES.PSYCHIC]: '🔮',
    [POKEMON_TYPES.FIGHTING]: '👊',
    [POKEMON_TYPES.POISON]: '☠️',
    [POKEMON_TYPES.GROUND]: '🌍',
    [POKEMON_TYPES.ROCK]: '🪨',
    [POKEMON_TYPES.BUG]: '🐛',
    [POKEMON_TYPES.GHOST]: '👻',
    [POKEMON_TYPES.STEEL]: '⚙️',
    [POKEMON_TYPES.ICE]: '❄️',
    [POKEMON_TYPES.DRAGON]: '🐉',
    [POKEMON_TYPES.DARK]: '🌙',
    [POKEMON_TYPES.FAIRY]: '🧚',
    [POKEMON_TYPES.NORMAL]: '⚪',
    [POKEMON_TYPES.FLYING]: '🕊️'
  };
  
  return typeIcons[type] || '❓';
};

export const formatAIMessage = (template: string, variables: Record<string, string>): string => {
  return template.replace(/\{(\w+)\}/g, (match, key) => variables[key] || match);
};

// ===========================================
// EDUCATIONAL CONTENT
// ===========================================

export const EDUCATIONAL_SCENARIOS = {
  TYPE_ADVANTAGE_BASIC: {
    title: 'Basic Type Advantages',
    scenarios: [
      {
        situation: 'Fire vs Grass',
        explanation: 'Fire burns grass easily - Fire attacks do 2x damage!',
        example: 'Charmander\'s Ember vs Bulbasaur',
        concept: AI_EDUCATION.CONCEPTS.PATTERN_RECOGNITION
      },
      {
        situation: 'Water vs Fire', 
        explanation: 'Water puts out fire - Water attacks do 2x damage!',
        example: 'Squirtle\'s Water Gun vs Charmander',
        concept: AI_EDUCATION.CONCEPTS.PATTERN_RECOGNITION
      }
    ]
  },
  
  AI_STRATEGIC_THINKING: {
    title: 'How AI Makes Strategic Decisions',
    scenarios: [
      {
        situation: 'Low HP Pokemon',
        aiDecision: 'Retreat to bench and switch to a healthier Pokemon',
        explanation: 'AI calculates survival probability and makes tactical switches',
        concept: AI_EDUCATION.CONCEPTS.STRATEGIC_THINKING
      },
      {
        situation: 'Type disadvantage',
        aiDecision: 'Switch Pokemon or use different strategy',
        explanation: 'AI recognizes unfavorable matchups and adapts',
        concept: AI_EDUCATION.CONCEPTS.DECISION_MAKING
      }
    ]
  }
};

// Default game state for initialization
export const createInitialGameState = () => ({
  currentTurn: 'child' as const,
  gamePhase: 'playing' as const,
  childPlayer: {
    name: 'Ash',
    activePokemon: SAMPLE_POKEMON[0], // Charmander
    benchedPokemon: [SAMPLE_POKEMON[2]], // Bulbasaur
    hand: [SAMPLE_POKEMON[3]], // Pikachu
    prizeCards: 6
  },
  aiPlayer: {
    name: 'Pokemon AI',
    activePokemon: SAMPLE_POKEMON[1], // Squirtle
    benchedPokemon: [SAMPLE_POKEMON[3]], // Pikachu
    hand: [],
    prizeCards: 6
  },
  winner: null,
  turnNumber: 1
});

export const createInitialAIThought = () => ({
  thinking: false,
  message: '',
  explanation: '',
  typeLesson: '',
  strategicInsight: ''
});

export const INITIAL_GAME_LOG = [
  '🎮 Pokemon TCG AI Education Battle Started!',
  '🔥 Charmander vs 💧 Squirtle - Type matchup analysis loading...',
  '🤖 AI is ready to demonstrate strategic thinking!'
];