import { mutation } from "./_generated/server";

export default mutation(({ db }, body, author) => {
  const message = { body, author };
  await db.insert("messages", message);
});
