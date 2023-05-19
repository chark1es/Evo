import { ActivityType } from "discord.js";

const { Client, IntentsBitField } = require("discord.js");
require("dotenv").config();

const client = new Client({
  intents: [
    IntentsBitField.Flags.Guilds,
    IntentsBitField.Flags.GuildMembers,
    IntentsBitField.Flags.GuildMessages,
    IntentsBitField.Flags.MessageContent,
  ],
});

client.on("interactionCreate", (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  if (interaction.commandName == "ping") {
    interaction.reply("pong");
  }

  if (interaction.commandName == "add") {
    const num1 = interaction.options.get("first_number")?.value;
    const num2 = interaction.options.get("second_number")?.value;
    interaction.reply(`The sum is ${num1 + num2}`);
  }
});

client.on("ready", (c) => {
  console.log(`${c.user.tag} is online`);

  client.user.setActivity({
    name: "Development Process",
    type: ActivityType.Streaming,
    url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  });
});

client.login(process.env.CLIENT_TOKEN);
