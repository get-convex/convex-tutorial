import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../convex/_generated/api';
import { GameState, Player, Card } from './types';

// Fixed cardTypes with consistent properties
const cardTypes: Omit<Card, 'cardId' | 'selected'>[] = [
  { type: '🐱', name: 'Cat', effect: 'See Future', color: '#4ecdc4', isAction: true },
  { type: '🐶', name: 'Dog', effect: 'Nope', color: '#ff6b6b', isAction: true },
  { type: '🌮', name: 'Taco', effect: 'Shuffle', color: '#f39c12', isAction: true },
  { type: '🍺', name: 'Beer', effect: 'Skip', color: '#9b59b6', isAction: true },
  { type: '⚡', name: 'Laser', effect: 'Attack', color: '#e67e22', isAction: true },
  { type: '⏰', name: 'Time', effect: 'Target', color: '#3498db', isAction: true },
  { type: '💤', name: 'Sleep', effect: 'Skip', color: '#95a5a6', isAction: true },
  { type: '👉', name: 'Point', effect: 'Target', color: '#e74c3c', isAction: true },
  { type: '💣', name: 'Bomb', effect: 'Exploding Kitten', color: '#e74c3c', isExploding: true, isAction: false },
  { type: '🔧', name: 'Defuse', effect: 'Defuse', color: '#2ecc71', isDefuse: true, isAction: false }
];

const agentTypes = [
  { id: 'bayesian', name: 'Bayesian Updating', color: '#667eea' },
  { id: 'qlearning', name: 'Q-Learning', color: '#f093fb' },
  { id: 'mle', name: 'Maximum Likelihood', color: '#4facfe' },
  { id: 'random', name: 'Random', color: '#fa709a' }
];

function App() {
    const [gameState, setGameState] = useState<GameState>({
      status: 'setup',
      currentPlayerIndex: 0,
      roundNumber: 1,
      players: [],
      deck: [],
      discardPile: [],
      playerHands: [],
      humanPlayerIndex: 0,
      maxPlayers: 5,
      bombPool: [],
      defusePool: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      createdBy: 'user',
      actionHistory: []
    });
  
  const [selectedCardIndex, setSelectedCardIndex] = useState(-1);
  const [gameStatus, setGameStatus] = useState('Welcome to Exploding Kittens! Click a position above to start.');
  const [showGameOverModal, setShowGameOverModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [gameOverMessage, setGameOverMessage] = useState('');

    // Helper function to check if game is over
  const isGameOver = useCallback(() => {
    return gameState.status === 'finished';
  }, [gameState.status]);

    // Convex operations
  const createGameMutation = useMutation(api.games.createGame);
  const playCardMutation = useMutation(api.games.playCard);
  const drawCardMutation = useMutation(api.games.drawCard);

  // Card ID counter
  let cardIdCounter = 0;

  const generateCardId = () => `card_${cardIdCounter++}`;

  const initializePlayers = useCallback((): Player[] => {
    const players: Player[] = [
      { 
        index: 0, name: 'You', type: 'human', avatar: '👤', 
        hand: [], defuseCards: 0, isAlive: true, isCurrentTurn: false, 
        handVisible: true, stats: {cardsDrawn: 0, cardsPlayed: 0, explosions: 0, wins: 0}, 
        hasDrawnThisTurn: false 
      },
      { 
        index: 1, name: 'Bayesian Agent', type: 'bayesian', avatar: '🧮', 
        hand: [], defuseCards: 0, isAlive: true, isCurrentTurn: false, handVisible: false, 
        stats: {cardsDrawn: 0, cardsPlayed: 0, explosions: 0, wins: 0}, 
        hasDrawnThisTurn: false 
      },
      { 
        index: 2, name: 'Q-Learning Agent', type: 'qlearning', avatar: '🔄', 
        hand: [], defuseCards: 0, isAlive: true, isCurrentTurn: false, handVisible: false, 
        stats: {cardsDrawn: 0, cardsPlayed: 0, explosions: 0, wins: 0}, 
        hasDrawnThisTurn: false 
      },
      { 
        index: 3, name: 'MLE Agent', type: 'mle', avatar: '📈', 
        hand: [], defuseCards: 0, isAlive: true, isCurrentTurn: false, handVisible: false, 
        stats: {cardsDrawn: 0, cardsPlayed: 0, explosions: 0, wins: 0}, 
        hasDrawnThisTurn: false 
      },
      { 
        index: 4, name: 'Random Agent', type: 'random', avatar: '🎲', 
        hand: [], defuseCards: 0, isAlive: true, isCurrentTurn: false, handVisible: false, 
        stats: {cardsDrawn: 0, cardsPlayed: 0, explosions: 0, wins: 0}, 
        hasDrawnThisTurn: false 
      }
    ];
    return players;
  }, []);

  const createDeck = useCallback((): Card[] => {
    const deck: Card[] = [];
    const regularTypes = cardTypes.slice(0, 8);
    
    for (let r = 0; r < 8; r++) {
      regularTypes.forEach((ct, idx) => {
        const cardData = { ...ct };
        deck.push({ 
          ...cardData,
          cardId: generateCardId()
        } as Card);
      });
    }
    
    return shuffleArray(deck);
  }, []);

  const shuffleArray = <T,>(array: T[]): T[] => {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
  };

  const startGame = useCallback(async () => {
    const players = initializePlayers();
    const deck = createDeck();
    
    // Deal initial hands
    const dealtPlayers = players.map(player => ({
      ...player,
      hand: deck.splice(0, 7),
      defuseCards: 1
    }));

    try {
      await createGameMutation({
        humanPlayerIndex: gameState.humanPlayerIndex,
        playerNames: players.map(p => p.name)
      });
    } catch (error) {
      console.error('Failed to create game:', error);
    }

    setGameState(prev => ({
      ...prev,
      players: dealtPlayers,
      deck,
      status: 'playing', // Use status instead of gameOver
      currentPlayerIndex: gameState.humanPlayerIndex,
      updatedAt: Date.now()
    }));

    setGameStatus('Game started! Play cards, then click DRAW to end your turn.');
  }, [gameState.humanPlayerIndex, initializePlayers, createDeck, createGameMutation]);

  const selectCard = useCallback((index: number) => {
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    if (isGameOver() || !currentPlayer || currentPlayer.type !== 'human') return;

    if (index === -1) {
      setSelectedCardIndex(-1);
    } else if (index >= 0 && index < currentPlayer.hand.length) {
      setSelectedCardIndex(index);
    }
  }, [gameState, isGameOver]);


  const drawCard = useCallback(async () => {
    if (isGameOver() || gameState.deck.length === 0) return;
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    if (!currentPlayer || !currentPlayer.isAlive || currentPlayer.type !== 'human') return;

    try {
      await drawCardMutation({
        gameId: '' as any,
        playerIndex: gameState.currentPlayerIndex
      });
    } catch (error) {
      console.error('Failed to draw card:', error);
    }

    if (gameState.deck.length > 0) {
      const newDeck = [...gameState.deck];
      const drawnCard = newDeck.shift()!;
      
      const updatedPlayers = [...gameState.players];
      updatedPlayers[gameState.currentPlayerIndex] = {
        ...updatedPlayers[gameState.currentPlayerIndex],
        hand: [...updatedPlayers[gameState.currentPlayerIndex].hand, drawnCard],
        hasDrawnThisTurn: true,
        stats: {
          ...updatedPlayers[gameState.currentPlayerIndex].stats,
          cardsDrawn: updatedPlayers[gameState.currentPlayerIndex].stats.cardsDrawn + 1
        }
      };

      setGameState(prev => ({
        ...prev,
        deck: newDeck,
        players: updatedPlayers,
        updatedAt: Date.now()
      }));

      setGameStatus(`You drew: ${drawnCard.name}`);
    }
  }, [gameState, drawCardMutation, isGameOver]);

  const playCard = useCallback(async () => {
    if (selectedCardIndex < 0) return;
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    if (!currentPlayer || currentPlayer.type !== 'human') return;
    
    const card = currentPlayer.hand[selectedCardIndex];
    if (!card) return;

    try {
      await playCardMutation({
        gameId: '' as any,
        playerIndex: gameState.currentPlayerIndex,
        cardIndex: selectedCardIndex
      });
    } catch (error) {
      console.error('Failed to play card:', error);
    }

    const updatedPlayers = [...gameState.players];
    const newHand = [...currentPlayer.hand];
    newHand.splice(selectedCardIndex, 1);
    
    updatedPlayers[gameState.currentPlayerIndex] = {
      ...currentPlayer,
      hand: newHand,
      stats: {
        ...currentPlayer.stats,
        cardsPlayed: currentPlayer.stats.cardsPlayed + 1
      }
    };

    const newDiscardPile = [card, ...gameState.discardPile];

    setGameState(prev => ({
      ...prev,
      players: updatedPlayers,
      discardPile: newDiscardPile,
      updatedAt: Date.now()
    }));

    setSelectedCardIndex(-1);
    setGameStatus(`You played ${card.name}`);
  }, [gameState, selectedCardIndex, playCardMutation]);

  const endTurn = useCallback(() => {
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    if (!currentPlayer) return;
    
    setGameStatus(`${currentPlayer.name} ends turn without drawing.`);
    // Add turn logic here
  }, [gameState]);

  const newGame = useCallback(() => {
    setGameState({
      status: 'setup',
      currentPlayerIndex: 0,
      roundNumber: 1,
      players: [],
      deck: [],
      discardPile: [],
      playerHands: [],
      humanPlayerIndex: 0,
      maxPlayers: 5,
      bombPool: [],
      defusePool: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      createdBy: 'user',
      actionHistory: [],
    });
    setSelectedCardIndex(-1);
    setGameStatus('Choose your position and start a new game!');
    setShowGameOverModal(false);
    setShowStatsModal(false);
  }, []);

  const updateHumanPlayerPosition = useCallback((position: number) => {
    setGameState(prev => ({ ...prev, humanPlayerIndex: position }));
  }, []);

  const renderPlayerSlots = () => {
    const positions = [
      { position: 0, name: '👤 You (Human)', type: 'Human Player' },
      { position: 1, name: '🤖 Bayesian Agent', type: 'Bayesian Updating' },
      { position: 2, name: '🤖 Q-Learning Agent', type: 'Q-Learning' },
      { position: 3, name: '🤖 MLE Agent', type: 'Maximum Likelihood' },
      { position: 4, name: '🎲 Random Agent', type: 'Random Choices' }
    ];

    return (
      <div className="game-setup">
        <h2 style={{ textAlign: 'center', color: '#2c3e50', marginBottom: '1rem' }}>
          Choose Your Position
        </h2>
        
        <div className="setup-row">
          {positions.slice(0, 2).map(pos => (
            <div
              key={pos.position}
              className={`player-slot ${gameState.humanPlayerIndex === pos.position ? 'active' : 'ai'}`}
              onClick={() => updateHumanPlayerPosition(pos.position)}
            >
              <span className="player-name">{pos.name}</span>
              <span className="agent-type">{pos.type}</span>
            </div>
          ))}
        </div>

        <div className="setup-row">
          {positions.slice(2, 4).map(pos => (
            <div
              key={pos.position}
              className={`player-slot ${gameState.humanPlayerIndex === pos.position ? 'active' : 'ai'}`}
              onClick={() => updateHumanPlayerPosition(pos.position)}
            >
              <span className="player-name">{pos.name}</span>
              <span className="agent-type">{pos.type}</span>
            </div>
          ))}
        </div>

        <div className="setup-row">
          <div
            className={`player-slot ${gameState.humanPlayerIndex === 4 ? 'active' : 'ai'}`}
            onClick={() => updateHumanPlayerPosition(4)}
          >
            <span className="player-name">{positions[4].name}</span>
            <span className="agent-type">{positions[4].type}</span>
          </div>
          <button className="btn" onClick={startGame}>Start Game!</button>
        </div>
      </div>
    );
  };

  const renderPlayerHand = () => {
    const currentPlayer = gameState.players[gameState.currentPlayerIndex];
    if (!currentPlayer || currentPlayer.type !== 'human' || !currentPlayer.isAlive) {
      return (
        <div className="player-hand">
          <div style={{ textAlign: 'center', color: '#666', padding: '2rem', width: '100%' }}>
            {currentPlayer?.isAlive ? "AI Player's Turn - Please Wait 🤖" : "Player Eliminated"}
          </div>
        </div>
      );
    }

    return (
      <div className="player-hand">
        {currentPlayer.hand.map((card, index) => (
          <div
            key={card.cardId}
            className={`card ${selectedCardIndex === index ? 'selected' : ''}`}
            onClick={() => selectCard(index)}
          >
            <div className="card-type" style={{ color: card.color || '#333' }}>
              {card.type}
            </div>
            <div className="card-effect">
              {card.name}<br /><small>{card.effect}</small>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderPlayerPanels = () => {
    return (
      <div className="players-container">
        {gameState.players.map((player, index) => {
          if (!player.isAlive) return null;
          
          const agentType = agentTypes.find(at => at.id === player.type) || 
            { name: 'Human', color: '#4ecdc4' };

          return (
            <div
              key={player.index}
              className={`player-panel ${player.isCurrentTurn ? 'current-turn' : ''} ${player.type !== 'human' ? 'ai-thinking' : ''}`}
            >
              <div 
                className={`player-avatar ${player.type}`}
                style={{ 
                  background: `linear-gradient(135deg, ${agentType.color}, ${adjustColor(agentType.color, -20)})` 
                }}
              >
                {player.avatar}
              </div>
              <div className="player-name-display">{player.name}</div>
              <div className="player-type">{agentType.name}</div>
              <div className="player-stats">
                <div className="stat">
                  <div className="stat-label">Cards</div>
                  <div className="stat-value">{player.hand.length}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Defuses</div>
                  <div className="stat-value">{player.defuseCards}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Status</div>
                  <div className={`stat-value ${player.isAlive ? 'alive' : 'dead'}`}>
                    {player.isAlive ? '🟢 Alive' : '💀 Exploded'}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const adjustColor = (color: string, amount: number): string => {
    try {
      const num = parseInt(color.replace("#", ""), 16);
      const amt = Math.round(2.55 * amount);
      const R = (num >> 16) + amt;
      const G = (num >> 8 & 0x00FF) + amt;
      const B = (num & 0x0000FF) + amt;
      return "#" + (0x1000000 + 
        (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + 
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + 
        (B < 255 ? B < 1 ? 0 : B : 255)
      ).toString(16).slice(1);
    } catch (e) {
      return color;
    }
  };

  const canPlayCard = selectedCardIndex >= 0 && 
    gameState.players[gameState.currentPlayerIndex]?.type === 'human' &&
    !isGameOver();

  const canDrawCard = gameState.deck.length > 0 && 
    gameState.players[gameState.currentPlayerIndex]?.type === 'human' &&
    !isGameOver();

  return (
    <div className="app">
      <header className="header">
        <h1>🧨 Exploding Kittens AI Arena</h1>
        <p>Play against 4 different AI strategies in the ultimate card game showdown!</p>
      </header>

      <div className="container">
        {gameState.status === 'setup' && renderPlayerSlots()}

        <div className={`game-board ${gameState.status === 'playing' ? 'active' : ''}`}>
          {gameState.status === 'playing' && renderPlayerPanels()}

          <div className="game-area">
            <div className="central-area">
              <div className="deck-area">
                <div className="deck-count">
                  {gameState.deck.length} cards remaining
                </div>
                <div 
                  className={`deck-pile ${!canDrawCard ? 'disabled' : ''}`}
                  onClick={canDrawCard ? drawCard : undefined}
                />
              </div>
              <div className="discard-pile">
                {gameState.discardPile.length > 0 && (
                  <div className="top-discard-card">
                    <div 
                      className="card-type" 
                      style={{ color: gameState.discardPile[0].color || '#333' }}
                    >
                      {gameState.discardPile[0].type}
                    </div>
                    <div className="card-effect">{gameState.discardPile[0].name}</div>
                  </div>
                )}
              </div>
            </div>

            {renderPlayerHand()}

            <div className="controls">
              <button 
                className="btn" 
                onClick={playCard}
                disabled={!canPlayCard}
              >
                {selectedCardIndex >= 0 
                  ? `Play ${gameState.players[gameState.currentPlayerIndex]?.hand[selectedCardIndex]?.name || 'Card'}`
                  : 'Play Selected Card'
                }
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={endTurn}
                style={{ display: selectedCardIndex >= 0 ? 'none' : 'inline-block' }}
                disabled={isGameOver()}
              >
                End Turn
              </button>
              <button className="btn btn-secondary" onClick={() => setShowStatsModal(true)}>
                Game Stats
              </button>
              <button className="btn btn-secondary" onClick={newGame}>
                New Game
              </button>
            </div>
          </div>

          <div className="game-status">
            {gameState.players[gameState.currentPlayerIndex]?.type !== 'human' ? (
              <div className="ai-thinking-indicator">
                <span className="spinner"></span>
                {gameState.players[gameState.currentPlayerIndex]?.name} is thinking...
              </div>
            ) : (
              gameStatus
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showGameOverModal && (
        <div className="modal active">
          <div className="modal-content">
            <h2>Game Over!</h2>
            <p>{gameOverMessage}</p>
            <button className="btn" onClick={newGame}>Play Again</button>
          </div>
        </div>
      )}

      {showStatsModal && (
        <div className="modal active">
          <div className="modal-content stats-modal-content">
            <h2>📊 Game Statistics</h2>
            <p>Performance metrics for all players</p>
            <div className="stats-grid">
              {gameState.players.map(player => {
                const agentType = agentTypes.find(at => at.id === player.type) || { name: 'Human' };
                return (
                  <div key={player.index} className="stat-card">
                    <h3>{player.name}<br /><small>{agentType.name}</small></h3>
                    <p>Wins: {player.stats.wins}</p>
                    <p>Explosions: {player.stats.explosions}</p>
                    <p>Cards Drawn: {player.stats.cardsDrawn}</p>
                    <p>Cards Played: {player.stats.cardsPlayed}</p>
                    <p>Defuses: {player.defuseCards}</p>
                    {player.isAlive ? 
                      <p style={{ color: '#27ae60', fontWeight: 'bold' }}>🟢 ALIVE</p> : 
                      <p style={{ color: '#e74c3c', fontWeight: 'bold' }}>💀 ELIMINATED</p>
                    }
                  </div>
                );
              })}
            </div>
            <button className="btn" onClick={() => setShowStatsModal(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;