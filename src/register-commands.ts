const { REST, Routes, ApplicationCommandOptionType } = require("discord.js");
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
  {
    name: "add",
    description: "Adds two numbers",
    options: [
      {
        name: "first_number",
        description: "First Number",
        type: ApplicationCommandOptionType.Number,
        required: true,
      },
      {
        name: "second_number",
        description: "First Number",
        type: ApplicationCommandOptionType.Number,
        required: true,
      },
    ],
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
