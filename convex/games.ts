import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const createGame = mutation({
  args: {
    humanPlayerIndex: v.number(),
    playerNames: v.array(v.string())
  },
  handler: async (ctx, args) => {
    // Initialize game state
    const gameId = await ctx.db.insert("games", {
      status: "setup",
      currentPlayerIndex: 0,
      roundNumber: 1,
      players: [],
      deck: [],
      discardPile: [],
      playerHands: [],
      humanPlayerIndex: args.humanPlayerIndex,
      maxPlayers: 5,
      bombPool: [],
      defusePool: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      createdBy: "user", // You might want to get this from auth
      actionHistory: []
      // Remove gameOver: false - use status instead
    });
    
    return gameId;
  }
});

export const getGame = query({
  args: { gameId: v.id("games") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.gameId);
  }
});

export const getActiveGames = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("games")
      .filter(q => q.neq(q.field("status"), "finished"))
      .order("desc")
      .take(10);
  }
});

export const playCard = mutation({
  args: {
    gameId: v.id("games"),
    playerIndex: v.number(),
    cardIndex: v.number()
  },
  handler: async (ctx, args) => {
    const game = await ctx.db.get(args.gameId);
    if (!game) throw new Error("Game not found");
    
    // Update game state - add your card playing logic here
    await ctx.db.patch(args.gameId, {
      updatedAt: Date.now()
    });

    // Add to action history
    await ctx.db.insert("playerActions", {
      gameId: args.gameId,
      playerIndex: args.playerIndex,
      actionType: "play_card",
      cardIndex: args.cardIndex,
      timestamp: Date.now(),
      processed: true
    });
  }
});

export const drawCard = mutation({
  args: {
    gameId: v.id("games"),
    playerIndex: v.number()
  },
  handler: async (ctx, args) => {
    const game = await ctx.db.get(args.gameId);
    if (!game) throw new Error("Game not found");
    
    // Update game state - add your draw card logic here
    await ctx.db.patch(args.gameId, {
      updatedAt: Date.now()
    });

    // Add to action history
    await ctx.db.insert("playerActions", {
      gameId: args.gameId,
      playerIndex: args.playerIndex,
      actionType: "draw_card",
      timestamp: Date.now(),
      processed: true
    });
  }
});

export const endTurn = mutation({
  args: {
    gameId: v.id("games"),
    playerIndex: v.number()
  },
  handler: async (ctx, args) => {
    const game = await ctx.db.get(args.gameId);
    if (!game) throw new Error("Game not found");

    // Calculate next player
    const nextPlayerIndex = (args.playerIndex + 1) % game.maxPlayers;
    
    await ctx.db.patch(args.gameId, {
      currentPlayerIndex: nextPlayerIndex,
      updatedAt: Date.now()
    });

    await ctx.db.insert("playerActions", {
      gameId: args.gameId,
      playerIndex: args.playerIndex,
      actionType: "end_turn",
      timestamp: Date.now(),
      processed: true
    });
  }
});

export const endGame = mutation({
  args: {
    gameId: v.id("games"),
    winnerIndex: v.number()
  },
  handler: async (ctx, args) => {
    const game = await ctx.db.get(args.gameId);
    if (!game) throw new Error("Game not found");

    await ctx.db.patch(args.gameId, {
      status: "finished",
      winner: args.winnerIndex,
      updatedAt: Date.now()
    });

    // Update player stats
    await ctx.db.insert("gameStats", {
      gameId: args.gameId,
      playerIndex: args.winnerIndex,
      playerType: game.players[args.winnerIndex]?.type || "unknown",
      finalPosition: 1,
      cardsDrawnTotal: game.players[args.winnerIndex]?.stats.cardsDrawn || 0,
      cardsPlayedTotal: game.players[args.winnerIndex]?.stats.cardsPlayed || 0,
      explosionsCaused: game.players[args.winnerIndex]?.stats.explosions || 0,
      defusesUsed: game.players[args.winnerIndex]?.defuseCards || 0,
      gameDuration: Date.now() - game.createdAt,
      win: true
    });
  }
});

export const getGameActions = query({
  args: { gameId: v.id("games") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("playerActions")
      .filter(q => q.eq(q.field("gameId"), args.gameId))
      .order("desc")
      .take(50);
  }
});