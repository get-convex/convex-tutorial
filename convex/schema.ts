import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  games: defineTable({
    // Game state
    status: v.union(
      v.literal("setup"),
      v.literal("playing"), 
      v.literal("finished")
    ),
    currentPlayerIndex: v.number(),
    roundNumber: v.number(),
    
    // Player information
    players: v.array(v.object({
      index: v.number(),
      name: v.string(),
      type: v.union(
        v.literal("human"),
        v.literal("bayesian"), 
        v.literal("qlearning"),
        v.literal("mle"),
        v.literal("random")
      ),
      avatar: v.string(),
      isAlive: v.boolean(),
      isCurrentTurn: v.boolean(),
      handVisible: v.boolean(),
      hasDrawnThisTurn: v.boolean(),
      defuseCards: v.number(),
      
      // Player statistics
      stats: v.object({
        cardsDrawn: v.number(),
        cardsPlayed: v.number(),
        explosions: v.number(),
        wins: v.number()
      }),
      
      // AI-specific state
      bayesianState: v.optional(v.any()),
      qLearningState: v.optional(v.any()),
      mleState: v.optional(v.any())
    })),
    
    // Card locations
    deck: v.array(v.object({
      cardId: v.string(),
      type: v.string(),
      name: v.string(), 
      effect: v.string(),
      color: v.string(),
      isAction: v.boolean(),
      isExploding: v.optional(v.boolean()),
      isDefuse: v.optional(v.boolean())
    })),
    
    discardPile: v.array(v.object({
      cardId: v.string(),
      type: v.string(),
      name: v.string(),
      effect: v.string(),
      color: v.string(),
      isAction: v.boolean(),
      isExploding: v.optional(v.boolean()),
      isDefuse: v.optional(v.boolean()),
      playedBy: v.optional(v.number()), // Player index who played this card
      playedAt: v.optional(v.number()) // Timestamp
    })),
    
    // Player hands (stored separately for security)
    playerHands: v.array(v.object({
      playerIndex: v.number(),
      cards: v.array(v.object({
        cardId: v.string(),
        type: v.string(),
        name: v.string(),
        effect: v.string(),
        color: v.string(),
        isAction: v.boolean(),
        isExploding: v.optional(v.boolean()),
        isDefuse: v.optional(v.boolean())
      }))
    })),
    
    // Game configuration
    humanPlayerIndex: v.number(),
    maxPlayers: v.number(),
    
    // Special card pools
    bombPool: v.array(v.object({
      cardId: v.string(),
      type: v.string(),
      name: v.string(),
      effect: v.string(),
      color: v.string(),
      isExploding: v.boolean()
    })),
    
    defusePool: v.array(v.object({
      cardId: v.string(),
      type: v.string(), 
      name: v.string(),
      effect: v.string(),
      color: v.string(),
      isDefuse: v.boolean()
    })),
    
    // Game metadata
    createdAt: v.number(),
    updatedAt: v.number(),
    createdBy: v.string(), // User ID or session ID
    winner: v.optional(v.number()), // Index of winning player
    
    // Game history for replay/analytics
    actionHistory: v.array(v.object({
      type: v.union(
        v.literal("draw"),
        v.literal("play"),
        v.literal("explode"),
        v.literal("defuse"),
        v.literal("turn_start"),
        v.literal("turn_end")
      ),
      playerIndex: v.number(),
      cardId: v.optional(v.string()),
      cardType: v.optional(v.string()),
      targetPlayer: v.optional(v.number()),
      timestamp: v.number(),
      description: v.string()
    }))
  })
  .index("by_status", ["status"])
  .index("by_createdAt", ["createdAt"])
  .index("by_createdBy", ["createdBy"]),

  // Separate table for active player actions (for real-time updates)
  playerActions: defineTable({
    gameId: v.id("games"),
    playerIndex: v.number(),
    actionType: v.union(
      v.literal("select_card"),
      v.literal("play_card"),
      v.literal("draw_card"),
      v.literal("end_turn"),
      v.literal("defuse_bomb"),
      v.literal("use_power")
    ),
    cardId: v.optional(v.string()),
    cardIndex: v.optional(v.number()),
    targetPlayer: v.optional(v.number()),
    timestamp: v.number(),
    processed: v.boolean() // Whether the action has been processed by game logic
  })
  .index("by_gameId", ["gameId"])
  .index("by_gameId_processed", ["gameId", "processed"]),

  // Game statistics and analytics
  gameStats: defineTable({
    gameId: v.id("games"),
    playerIndex: v.number(),
    playerType: v.string(),
    finalPosition: v.number(),
    cardsDrawnTotal: v.number(),
    cardsPlayedTotal: v.number(),
    explosionsCaused: v.number(),
    defusesUsed: v.number(),
    gameDuration: v.number(), // in seconds
    win: v.boolean()
  })
  .index("by_gameId", ["gameId"])
  .index("by_playerType", ["playerType"]),

  // AI agent state storage (for learning across games)
  aiAgentState: defineTable({
    agentType: v.string(),
    gameId: v.id("games"),
    stateData: v.any(), // Flexible storage for different AI types
    createdAt: v.number(),
    updatedAt: v.number()
  })
  .index("by_agentType", ["agentType"])
  .index("by_gameId", ["gameId"]),

  // User profiles and preferences
  userProfiles: defineTable({
    userId: v.string(),
    displayName: v.optional(v.string()),
    avatar: v.optional(v.string()),
    gamesPlayed: v.number(),
    gamesWon: v.number(),
    favoriteAgent: v.optional(v.string()),
    preferences: v.optional(v.object({
      soundEnabled: v.boolean(),
      animationsEnabled: v.boolean(),
      autoPlaySpeed: v.number()
    })),
    createdAt: v.number(),
    updatedAt: v.number()
  })
  .index("by_userId", ["userId"]),

  // Session management for anonymous players
  gameSessions: defineTable({
    sessionId: v.string(),
    userId: v.optional(v.string()),
    currentGameId: v.optional(v.id("games")),
    lastActivity: v.number(),
    userAgent: v.optional(v.string()),
    createdAt: v.number()
  })
  .index("by_sessionId", ["sessionId"])
  .index("by_lastActivity", ["lastActivity"])
});