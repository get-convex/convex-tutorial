// src/types.ts
export interface Card {
    cardId: string;
    type: string;
    name: string;
    effect: string;
    color: string;
    isAction: boolean;
    isExploding?: boolean;
    isDefuse?: boolean;
    selected?: boolean;
  }
  
  export interface PlayerStats {
    cardsDrawn: number;
    cardsPlayed: number;
    explosions: number;
    wins: number;
  }
  
  export interface Player {
    index: number;
    name: string;
    type: 'human' | 'bayesian' | 'qlearning' | 'mle' | 'random';
    avatar: string;
    hand: Card[];
    defuseCards: number;
    isAlive: boolean;
    isCurrentTurn: boolean;
    handVisible: boolean;
    stats: PlayerStats;
    hasDrawnThisTurn: boolean;
    bayesianState?: any;
    qLearningState?: any;
    mleState?: any;
  }
  
  export interface GameState {
    status: 'setup' | 'playing' | 'finished';
    currentPlayerIndex: number;
    roundNumber: number;
    players: Player[];
    deck: Card[];
    discardPile: Card[];
    playerHands: any[]; // Add this to match schema
    humanPlayerIndex: number;
    maxPlayers: number;
    bombPool: Card[];
    defusePool: Card[];
    createdAt: number;
    updatedAt: number;
    createdBy: string;
    winner?: number;
    actionHistory: any[];
  }