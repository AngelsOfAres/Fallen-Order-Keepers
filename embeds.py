import discord
import random

embedAdminOnly = discord.Embed(
                title="⛔ WOOPS! ⛔",
                description=f"This command is reserved for admins only!",
                color=0xFF1C0A,
            )

embedCD = discord.Embed(
            title=f"Damn! That's faster than block time chill!",
            description=f"Give it a second and try again...",
            color=0xFF1C0A,
            )

embedErr = discord.Embed(
                title="GET $EXP",
                url="https://vestige.fi/asset/811721471",
                description=f"You do not own that much $EXP 😔",
                color=0xFF1C0A,
            )

embedNoOptEXP = discord.Embed(
                title="You Are Not Opted Into $EXP!",
                description="[Click Here To Opt In...](https://www.randgallery.com/algo-collection/?address=811721471)",
                color=0xFF1C0A,
            )
embedNoOptEXP.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

embedNoOptORDER = discord.Embed(
                title="You Are Not Opted Into $ORDER!",
                description="[Click Here To Opt In...](https://www.randgallery.com/algo-collection/?address=811718424)",
                color=0xFF1C0A,
            )
embedNoOptORDER.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

embedNoOptRAFFLE = discord.Embed(
                title="You Are Not Opted Into $RAFFLE!",
                description="[Click Here To Opt In...](https://www.randgallery.com/algo-collection/?address=815766197)",
                color=0xFF1C0A,
            )
embedNoOptRAFFLE.set_image(url="https://nft-media.algoexplorerapi.io/images/bafkreiabe7amkqwuz6kip7xnx6c5bx7v73bw2qofuaoqhu23nufrwfnn4e")
embedNoOptRAFFLE.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

embedErr.set_footer(
    text='#Vestige',
    icon_url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/assets-logo-png/2022/10/11/a26da3af714a40e8bad2b29a6dfc4655.png--resize--w__200--q__70.webp"
            )

embedWrongChannel = discord.Embed(
            title=f"Gaming is restricted to House Of Hermes channels only",
            description=f"Please head over to that section to play! 🤑",
            color=0xFF1C0A
        )

embedWrongChannelDrip = discord.Embed(
            title=f"Drip Claims are restricted to any channel besides chatroom and alpha chat!",
            description=f"Please head over to any other channel to claim! 🤑",
            color=0xFF1C0A
        )

embedWrongChannelBoost = discord.Embed(
            title=f"Upgrades are restricted to the stat boost channel!",
            description=f"Please head over to the boost channel to upgrade!",
            color=0xFF1C0A
        )


embedLeaderboard = discord.Embed(title='Leaderboard - House Of Hermes', description='Those who have dared to take on Hermes:', color=0xFFFB0A)

embedStatsAdded = discord.Embed(
            title=f"🔥 ALL CHARACTER STATS HAVE BEEN INITIATED 🔥",
            color=discord.Color(random.randint(0, 0xFFFFFF))
        )
embedStatsAdded.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")    
embedStatsAdded.set_footer(text=f"Stats have been added successfully!")

embedNotKinshipChannel = discord.Embed(
            title=f"Kinship is restricted to Temple channel only",
            description=f"⚔️ Please head over to the kinship channel to cast ritual! ⚔️",
            color=0xFF1C0A
        )

embedKinshipAdded = discord.Embed(
                title=f"Kinship Ritual Successful!",
                description=f"The following Fallen Order characters were boosted",
                color=0xFCE303
            )
embedKinshipAdded.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

embedKinshipOn = discord.Embed(
                title=f"A Kinship Ritual is already in progress!",
                description=f"Please wait while other player completes their ritual...",
                color=0xFF0000
            )
embedKinshipOn.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

embedStatBoostOn = discord.Embed(
                title=f"A Stat Boost is already in progress!",
                description=f"Please wait while other player completes their upgrades...",
                color=0xFF0000
            )
embedStatBoostOn.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

embedNotBattleChannel = discord.Embed(
            title=f"Battling is restricted to Fallen Battles channel only",
            description=f"⚔️ Please head over to the battle channel to fight! ⚔️",
            color=0xFF1C0A
        )
embedNotBattleChannel.set_footer(text="Enjoy watching the battles above!")

embedMaxBattles = discord.Embed(
    title=f"There are 2 ongoing battles...!",
    description=f"Please wait while current battles end...",
    color=0xFF0000
)
embedMaxBattles.set_footer(text="Enjoy watching the battles above!")

embedDiscordErr = discord.Embed(
    title=f"Woops...seems the Discord API is having issues",
    description=f"Please try again, if the failure continues you may want to check back in a few minutes",
    color=0xFF0000
)

embedNoSelfBattle = discord.Embed(
                    title=f"You can not battle yourself...",
                    description=f"Find another player and try again!",
                    color=0xFF0000
                )
embedNoSelfBattle.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

embedNotDeathmatchChannel = discord.Embed(
    title=f"This command is restricted to Death Match channel only",
    description=f"⚔️ Please head over to the deathmatch channel to sign up! ⚔️",
    color=0xFF1C0A
)
embedNotDeathmatchChannel.set_footer(text="Must own a Fallen Order NFT to participate!")

embedNoFallen = discord.Embed(
            title=f"⛔ WOOPS! ⛔",
            description=f"You Do Not Hold Any Fallen Order NFTs..",
            color=0xFF1C0A
        )
embedNoFallen.set_footer(text="[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)")

embedNoFlex = discord.Embed(
    title=f"⛔ WOOPS! ⛔",
    description=f"You Do Not Hold Any Ghosts or Fallen Order NFTs..",
    color=0xFF1C0A
)
embedNoFlex.set_footer(text="[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)")

embedShuffle = discord.Embed(
    title=f"Fallen Order Shuffle",
    description="[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
    color=0xFF1C0A
)
embedShuffle.set_image(url="https://ipfs.algonft.tools/ipfs/QmfFTpw6MEKxpLGA1ZEjWoQdBVbYveCGZh84inaNs39LFn")
embedShuffle.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

embedAzazel = discord.Embed(
    title=f"Azazel, the Prince Of Hell",
    description=f"10000 HP\n\nAbilities:",
    color=0xFF1C0A
)
embedAzazel.set_image(url="https://i.ibb.co/5WCwkwN/Azazel.png")
embedAzazel.add_field(name=f"Smash", value=f"800-1200 damage", inline=False)
embedAzazel.add_field(name=f"Slap", value=f"600-800 damage", inline=False)
embedAzazel.add_field(name=f"Tail Whip", value=f"500-1000 damage", inline=False)
embedAzazel.add_field(name=f"Hellfire", value=f"800-2000 damage", inline=False)
embedAzazel.add_field(name=f"Dark Barrier", value=f"Blocks next 2 incoming attacks\n*Ultimates do not apply*", inline=False)
embedAzazel.add_field(name=f"Eruption", value=f"Sets enemy on fire for the next 3 rounds\nDeals 300-600 damage per round", inline=False)
embedAzazel.add_field(name=f"Tranquility", value=f"Restores 500-2000 hitpoints", inline=False)
embedAzazel.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
embedAzazel.set_footer(text="You think you can beat me? Pfft...\nShow me what you've got with /boss-battle! 👹")

embedMordekai = discord.Embed(
    title=f"Mordekai, Master Of Gheists",
    description=f"12000 HP\n\nAbilities:",
    color=0xFFFFFF
)
embedMordekai.set_image(url="https://i.ibb.co/Ry4VqBW/mordekai.jpg")
embedMordekai.add_field(name=f"Ghastly Vengeance", value=f"1000-1200 damage", inline=False)
embedMordekai.add_field(name=f"Ghost Army", value=f"700-900 damage", inline=False)
embedMordekai.add_field(name=f"Spirit Bomb", value=f"800-1200 damage", inline=False)
embedMordekai.add_field(name=f"Call Of The Undead", value=f"Restores 1000-2000 hitpoints", inline=False)
embedMordekai.add_field(name=f"Shadow Barrier", value=f"Blocks next 2 incoming attacks\n*Ultimates do not apply*", inline=False)
embedMordekai.add_field(name=f"Abyssal Curse", value=f"Sets a curse on the enemy for the next 3 rounds\nDeals 600-1000 damage per round", inline=False)
embedMordekai.add_field(name=f"Tremble", value=f"600-2000 damage", inline=False)
embedMordekai.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
embedMordekai.set_footer(text="You think you can beat me? Pfft...\nShow me what you've got with /boss-battle! 👻")

embedDrip = discord.Embed(
                title=f"💸 $EXP DRIP! 💸",
                footer=f"Next Claim In 6 Hours ⏱️",
                color=0x28FF0A,
                )
embedDrip.set_thumbnail(url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/assets-logo-png/2022/10/11/a26da3af714a40e8bad2b29a6dfc4655.png--resize--w__200--q__70.webp")
embedDrip.set_footer(text=f"Enjoy the games! 💛")

embedAdminRoles = discord.Embed(
                        title=f"Master, I've updated all roles in the server to their appropriate designation...",
                        description=f"Here is a breakdown of the changes I made:",
                        color=0xFFFB0A
                    )

embedAW = discord.Embed(
                title=f"Master, I've updated all counts for Angel Wing holders and sent the allocated drop!",
                color=0xFFFB0A
            )
embedAW.set_thumbnail(url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/asset_verification_requests_logo_png/2022/06/22/d2c56a8e61244bd78017e38180d15c91.png--resize--w__200--q__70.webp")

embedNoCount = discord.Embed(
            title=f"WOOPS!",
            description=f"Looks like you do not hold any assets from AoA..",
            color=0x00E1FF
        )
embedNoCount.set_footer(
        text='If you have any questions or concerns please tag @angel.algo 💙',
        icon_url="https://www.vesea.io/_next/image?url=https%3A%2F%2Fs3.us-east-2.amazonaws.com%2Fvesea.io-profiles%2Fprofile_pics%2F0xe3e0bb8fe0a2a65858eaa8c04758f14939ff2a95.WEBP%3Fr%3D352&w=960&q=75"
    )


embedCurrentSignUps = discord.Embed(
            title=f"💀 Current Death Match Sign Ups 💀",
            description=f"The following Fallen Order warriors have entered the Death Match:",
            color=0x28FF0A
        )
embedNoSignUps = discord.Embed(
            title=f"💀 Current Death Match Sign Ups 💀",
            description=f"There are currently no Fallen Order signed up for Death Match...",
            color=0x28FF0A
        )
embedCurrentSignUps.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
embedCurrentSignUps.set_footer(text=f"Once 5 sign ups are reached the Death Match will commence...")
embedNoSignUps.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
embedNoSignUps.set_footer(text=f"To sign up use the /deathmatch command!")

embedCommands1 = discord.Embed(
                title=f"Command Master List",
                description=f"There are many things Heimdall can help you with...",
                color=0x28FF0A
            )
embedCommands2 = discord.Embed(
                title=f"Command Master List",
                description=f"There are many things Heimdall can help you with...",
                color=0x28FF0A
            )
embedCommands3 = discord.Embed(
                title=f"Command Master List",
                description=f"There are many things Heimdall can help you with...",
                color=0x28FF0A
            )
embedCommands1.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
embedCommands1.add_field(name=f"General Commands", value=f'The following commands are for general use:', inline=False)
embedCommands1.add_field(name=f"/shuffle", value=f'Produces a link to the Fallen Order shuffle', inline=False)
embedCommands1.add_field(name=f"/roles", value=f'Register/Update your roles and produce a breakdown of your score', inline=False)
embedCommands1.add_field(name=f"/balance", value=f'Produce a detailed breakdown of your AoA holdings', inline=False)
embedCommands1.add_field(name=f"/tickets", value=f'Purchase $RAFFLE Tickets Using $ORDER/$EXP', inline=False)
embedCommands1.add_field(name=f"/flex", value=f'Show off your Fallen Order or Ghosts Of Algo NFTs', inline=False)
embedCommands1.add_field(name=f"/drip", value=f'Claim 1-5 $EXP for FREE every 6H', inline=False)
embedCommands1.add_field(name=f"/send", value=f'Transfer EXP/RAFFLE/ORDER to other users', inline=False)
embedCommands2.add_field(name=f"---------------------------------------------------\n\nHouse Of Hermes", value=f'The following commands are part of our casino which is open to the public:', inline=False)
embedCommands2.add_field(name=f"/leaderboard", value=f'Produce a sorted leaderboard of HoH games', inline=False)
embedCommands2.add_field(name=f"/stats", value=f'Produce a detailed breakdown of your personal HoH stats', inline=False)
embedCommands2.add_field(name=f"/dice", value=f'Play dice. Rolls a random number 1-100 against Hermes. If you are higher you win your $EXP bet. If you are lower you lose your bet. If you tie you hit the bullseye and double your bet.', inline=False)
embedCommands2.add_field(name=f"/blackjack", value=f'Play classic 21 Blackjack against Hermes.', inline=False)
embedCommands3.add_field(name=f"---------------------------------------------------\n\nFallen Order", value=f'The following commands are for use by Fallen Order holders only:', inline=False)
embedCommands3.add_field(name=f"/rename", value=f'Give your character a custom name!', inline=False)
embedCommands3.add_field(name=f"/main-character", value=f'Select your main character for Skills', inline=False)
embedCommands3.add_field(name=f"/equip-hatchet", value=f'Equip a Hatchet to chop trees', inline=False)
embedCommands3.add_field(name=f"/dequip-hatchet", value=f'Dequip a Hatchet from your account', inline=False)
embedCommands3.add_field(name=f"/replenish-hatchet", value=f"Add 100 Uses to your equipped Hatchet for 100 $EXP", inline=False)
embedCommands3.add_field(name=f"/chop", value=f"Chop trees to level up your main character's Woodcutting skill and earn logs/$EXP", inline=False)
embedCommands3.add_field(name=f"/bosses", value=f'Display breakdown of all available bosses and their abilities', inline=False)
embedCommands3.add_field(name=f"/boss-battle", value=f'Battle your Fallen Order character against a Boss!', inline=False)
embedCommands3.add_field(name=f"/boss-rankings", value=f'Display leaderboard of Boss Battle Points', inline=False)
embedCommands3.add_field(name=f"/kinship", value=f'Upgrade your Fallen Order characters kinship once every 24H', inline=False)
embedCommands3.add_field(name=f"/levelup", value=f"Level Up your Fallen Order characters and receive a Stat Booster NFT once up to once per hour", inline=False)
embedCommands3.add_field(name=f"/abilities", value=f"List all abilities and their breakdowns", inline=False)
embedCommands3.add_field(name=f"/swap-ability", value=f"Change your character's abilities and ultimate up to once per hour", inline=False)
embedCommands3.add_field(name=f"/boost", value=f"Use your character's available points to boost stats up to once per hour", inline=False)
embedCommands3.add_field(name=f"/use-booster", value=f"Use your Stat Booster $BOOST NFTs to add 50 Points to your character", inline=False)
embedCommands3.add_field(name=f"/battle", value=f'Battle your Fallen Order versus other players for $EXP bets', inline=False)
embedCommands3.add_field(name=f"/deathmatch", value=f'5 Fallen Order enter a Death Match for 50 $EXP each. They battle against Ares and the highest damage dealer takes all 250 $EXP', inline=False)
embedCommands1.set_footer(text=f"If you have suggestions for more features please tag @angel.algo!", icon_url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/asset_verification_requests_logo_png/2022/06/22/d2c56a8e61244bd78017e38180d15c91.png--resize--w__200--q__70.webp")
embedCommands2.set_footer(text=f"If you have suggestions for more features please tag @angel.algo!", icon_url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/asset_verification_requests_logo_png/2022/06/22/d2c56a8e61244bd78017e38180d15c91.png--resize--w__200--q__70.webp")
embedCommands3.set_footer(text=f"If you have suggestions for more features please tag @angel.algo!", icon_url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/asset_verification_requests_logo_png/2022/06/22/d2c56a8e61244bd78017e38180d15c91.png--resize--w__200--q__70.webp")

embedAbilities = discord.Embed(
                title=f"Fallen Order Abilities Master List",
                description=f"Many abilities to choose from...be wise!",
                color=0x28FF0A
            )
embedAbilities.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
embedAbilities.add_field(name=f"BASIC ABILITIES", value=f'Each character has 3 of the following abilities:', inline=False)
embedAbilities.add_field(name=f"Slash", value=f'Deals damage equal to 80-150% ATK', inline=False)
embedAbilities.add_field(name=f"Fury", value=f'Deals damage equal to 100-200% ATK', inline=False)
embedAbilities.add_field(name=f"Fireball", value=f'Deals damage equal to 80-150% AP', inline=False)
embedAbilities.add_field(name=f"Arcane Nova", value=f'Deals damage equal to 100-200% AP', inline=False)
embedAbilities.add_field(name=f"Retribution", value=f'Heals 75-200% of DEF', inline=False)
embedAbilities.add_field(name=f"Eclipse", value=f'Deals damage equal to 100-200% of half ATK + AP', inline=False)
embedAbilities.add_field(name=f"Purify", value=f'Reduce all negative effect tickers by 1', inline=False)
embedAbilities.add_field(name=f"Soul Surge", value=f'Deals damage equal to 200-300% of half ATK + AP\nInflicts 100-300 self-inflicted Surge damage', inline=False)
embedAbilities.add_field(name=f"---------------------------------------------------\n\nULTIMATES", value=f'Each character has 1 of the following ultimates:', inline=False)
embedAbilities.add_field(name=f"Death Blow", value=f'1/3 Chance of dealing 2500 damage\n50% chance of 250 self-inflicted damage', inline=False)
embedAbilities.add_field(name=f"Divine Aura", value=f"Heals 500-3000 hitpoints instantly", inline=False)
embedAbilities.add_field(name=f"Mirage", value=f"Blocks the next 2 incoming attacks", inline=False)
embedAbilities.add_field(name=f"Pestilence", value=f"Applies a Poison effect on the enemy dealing 100-300 damage for the next 3 rounds", inline=False)
embedAbilities.add_field(name=f"Molten Rage", value=f"Boosts your character's ATK | DEF | AP by 20% for the next 2 rounds", inline=False)
embedAbilities.set_footer(text=f"To swap your abilities use /swap-ability")