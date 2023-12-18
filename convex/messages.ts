import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

export const list = query(async (ctx) => {
  return await ctx.db.query("messages").collect();
});

export const send = mutation({
  args: { body: v.string(), author: v.string() },
  handler: async (ctx, { body, author }) => {
    const message = { body, author };
    await ctx.db.insert("messages", message);
  },
});

export const makeRefs = mutation(async (ctx) => {
  for (let i = 4; i >= 1; i--) {
    const id = await ctx.db.insert(("u" + i) as any, {});
    const o: any = {};
    o["u" + i] = id;
    await ctx.db.insert("references" as any, o);
    await ctx.db.delete(id);
  }
});
