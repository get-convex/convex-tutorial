// utils/stateEncoder.ts
import { GameState, Player } from '../types';

export class StateEncoder {
  static encodeState(gameState: GameState, playerIndex: number): number {
    const player = gameState.players[playerIndex];
    if (!player) return 0;
    
    // Simple state encoding based on your game
    let stateId = 0;
    
    // Encode player's hand composition (simplified)
    const handSize = Math.min(player.hand.length, 7); // Cap at 7
    stateId += handSize * 1;
    
    // Encode defuse cards
    stateId += Math.min(player.defuseCards, 5) * 10;
    
    // Encode deck size (approximate)
    const deckSize = Math.min(gameState.deck.length, 30);
    stateId += Math.floor(deckSize / 10) * 100;
    
    // Encode number of alive players
    const alivePlayers = gameState.players.filter(p => p.isAlive).length;
    stateId += (alivePlayers - 1) * 1000;
    
    // Encode player type
    const typeMultiplier = {
      'human': 0,
      'qlearning': 1,
      'mle': 2,
      'bayesian': 3,
      'random': 4
    }[player.type] || 0;
    
    stateId += typeMultiplier * 10000;
    
    // Ensure stateId fits within your policy size (100000)
    return stateId % 100000;
  }
}