const { REST, Routes } = require("discord.js");
require("dotenv").config();

const commands = [
  {
    name: "test",
    description: "test command",
  },
  {
    name: "ping",
    description: "pong",
  },
];

const rest = new REST({ version: "10" }).setToken(process.env.CLIENT_TOKEN);

(async () => {
  try {
    console.log("Registering Slash Commands");
    await rest.put(
      Routes.applicationGuildCommands(process.env.BOT_ID, process.env.GUILD_ID),
      { body: commands }
    );
    console.log("Commands have been registered successfully!");
  } catch (error) {
    console.log(`There is an error: ${error}`);
  }
})();
