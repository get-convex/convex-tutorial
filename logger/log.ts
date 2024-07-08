import { v } from "convex/values";
import { mutation } from "./_generated/server";

export const info = mutation({
  args: { message: v.string() },
  returns: v.null(),
  handler: async (ctx, args) => {
    console.log(args.message);
    await ctx.db.insert("lines", { message: args.message });
  },
});
