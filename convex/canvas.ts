import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const setCanvas = mutation({
  args: { body: v.string() },
  handler: async (ctx, args) => {
    const existing = await ctx.db.query("canvas").first();
    if (existing) {
      await ctx.db.patch(existing._id, { body: args.body });
    } else {
      await ctx.db.insert("canvas", { body: args.body });
    }
  },
});

export const getCanvas = query({
  args: {},
  handler: async (ctx) => {
    const existing = await ctx.db.query("canvas").first();
    return existing ?? { body: "" };
  },
});
