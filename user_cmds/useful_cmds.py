from shared_vars import commands, Server_stats, code_dict, discord, save_data, allowed_file_endings, months
from message_events.message_management import response_waiting
from user_cmds.cmds_logic import format_to_code, PIL_round_img_obj,PIL_text_obj
from io import BytesIO
from PIL import Image, ImageDraw
import aiohttp
from pathlib import Path
class Basic_cmds(commands.Cog):
    def __init__(self, client:commands.Bot,server_stats:Server_stats):
        self.client = client
        self.server_stats = server_stats
    @commands.command(help='This cmd gives you the code for the given code name.',brief='Gives code for the given name.')
    async def gen(self, ctx:commands.Context, user_input: str='help'): # TODO Make it so that you can do smth like gen(first command(if this command endswith : + 4 spaces , ; (go back four spaces,(, adds a newline))) ) also mayber add a gen cmd for another language
        #global code_dict
        all_descriptions = 'Avalible code is:'
        for description in code_dict.keys():
            if description == 'help':
                continue
            all_descriptions += '\n' + description
        code_dict['help'] = all_descriptions
        save_data('code',code_dict)
        if user_input in code_dict.keys():
            if len(code_dict[user_input]) < 2000:
                await ctx.send(code_dict[user_input])
            else:
                ram = BytesIO(code_dict[user_input].encode('UTF-8'))
                ram.name = f'{user_input}.py'#makes it so that discord treats it like a real file
                await ctx.send(file = discord.File(ram))
        else:
            if self.client.owner_id == ctx.author.id:
                await ctx.send('Would you like to add this code? (y/n)')
                response = await response_waiting(ctx,self.client)
                if response == None:
                    return
                if response.content.lower() == 'y':
                    await ctx.send('What is the code?')
                    code = await response_waiting(ctx, self.client,time = 180)
                    if response is None:
                        return 
                    if code.attachments and len(code.content.strip()) == 0:
                        if len(code.attachments) == 1:
                            if any(code.attachments[0].filename.lower().endswith(fileend) for fileend in allowed_file_endings):
                                content_in_bytes = await code.attachments[0].read()
                                try:
                                    code  = content_in_bytes.decode('UTF-8')
                                except UnicodeDecodeError:
                                    print(f'Error while trying to decode file')
                        if isinstance(code, discord.Message):
                            code = code.content
                    final_code = format_to_code(code, 'python')
                    code_dict[user_input] = final_code
                    save_data('code', code_dict)
                elif response.content.lower() == 'n':
                    return
            else:
                await ctx.send(f'This gen command does not exist.\nIf you want a list of all possible !gen commands enter !gen help.')
            
    @commands.command(help='This cmd adds the gen code to the gen options.',brief='Deletes the given gen cmd.')
    @commands.is_owner()
    async def gen_edit(self,ctx, user_input: str):
        #global code_dict
        if  ctx.author.id != self.client.owner_id:
            return #for when the cmd is called directly
        if user_input in code_dict.keys():
            await ctx.send('What would you like to change the code to?(Enter exit to exit.)')
            code = await response_waiting(ctx,self.client)
            if code == None:
                return
            if code.content == 'exit':
                return
            final_code = format_to_code(code.content)
            code_dict[user_input] = final_code
            save_data('code',code_dict)
        else:
            await ctx.send('This code description does not exist in the code dict.')
            
    @commands.command(help='This cmd deletes the given gen cmd from the gen dict.',brief='Deletes the given gen cmd.')
    @commands.is_owner() # TODO make it so that also higher roles than dev can acces this command also automaticly including all rules with admin acces and the owner
    async def gen_del(self, ctx, user_input: str):
        if  ctx.author.id != self.client.owner_id:
            return #for when the cmd is called directly
        #global code_dict
        if user_input in code_dict.keys():
            await ctx.send('Are you sure that you want to delete the code for this command? (y/n)')
            response = await response_waiting(ctx,self.client)
            if response == None:
                return
            if response.content == 'y':
                code_dict.pop(user_input)
            else:
                return
        else:
            await ctx.send('This code description does not exist in the code dict.')
    
    @commands.command(help='This cmd sends a stats card of the given user.',brief='Shows stats of the given user.')   
    async def stats(self, ctx:commands.Context, user: discord.Member = None):
        print(f'called stats with msg {ctx.message.id}')
        if user == None:
            member = ctx.author
        else:
            member = user
        guild = member.guild
        user_stats = self.server_stats.user_stats(guild)
        try:
            avatar_in_bytes = await member.display_avatar.read() if member.avatar else await member.default_avatar.read()
            rounded_img, mask = PIL_round_img_obj(avatar_in_bytes, (395,395))
            with Image.open(r'images/base.png','r') as img2:
                white_image = img2.copy()#.copy is absolutly needed here because it would else just reference the object that doesnt exist anymore because with closes it after
            white_image.paste(rounded_img, (7,85), mask=mask)
            width, height = white_image.size
            server = ctx.guild
            index = server.id % 5#this is the server icon discord chooses out of the 5 using the same line
            server_avatar_url = server.icon.url if server.icon else f'https://cdn.discordapp.com/embed/avatars/{index}.png'

            async with aiohttp.ClientSession() as session: #starts a new http session, use it with paragraphs to use the function not the class
                async with session.get(server_avatar_url) as site: #opens the icon or default server icon site
                    server_avatar_in_bytes = await site.read() 

            img2,mask = PIL_round_img_obj(server_avatar_in_bytes,(90,90))
            white_image.paste(img2,(535,125),mask=mask)            
            current_xp = user_stats.stats[member.id]['xp']
            try:
                xp_needed = self.server_stats.stats[guild.id]['roles_requirements'][next(k for k,v in self.server_stats.stats[guild.id]['server_roles'].items() if v == user_stats.stats[member.id]['next_rank'])]['xp']
            except (KeyError,StopIteration):
                xp_needed = ''
            txt_to_dp = f'XP: {current_xp}/{xp_needed}'
            if type(xp_needed) != int:
                if current_xp != 0:
                    xp_needed = current_xp
                else:
                    xp_needed = 1
                    current_xp = 1
                txt_to_dp = 'Max XP'
            draw = ImageDraw.Draw(white_image)
            progress= current_xp/xp_needed # Total_widht * progress = current xp / needed xp
            full_width = 500
            width_bar = int(full_width * progress)
            percent = f'{int(progress * 100)}%'
            height_bar = 25
            bar = Image.new('RGBA', (width_bar, height_bar), (9, 129, 209))
            for x in range(bar.width):
                if txt_to_dp == 'Max XP':
                    start_color = (187,155,73)
                    end_color = (255, 255, 200)
                else:
                    start_color = (0, 200, 255)
                    end_color = (120, 255, 255)
                percentage = x / (bar.width-1)
                bar_pixels = bar.load()
                r = int(start_color[0] + (end_color[0] - start_color[0]) * percentage)# it works because when it gets brighter the way is - so every time it removes more
                g = int(start_color[1] + (end_color[1] - start_color[1]) * percentage)# it takes the base and adds the way multiplied by how far to it
                b = int(start_color[2] + (end_color[2] - start_color[2]) * percentage)
                for y in range(bar.height):
                    bar_pixels[x,y] = (r,g,b)

            mask = Image.new('L', (width_bar, height_bar), 0)
            x= int(width/2)
            y = int(height/2.5)
            cords = x,y
            bar_cords = x+width_bar,y-2.5
            radius = height_bar//2 
            draw = ImageDraw.Draw(mask)#makes it possible to draw on the image mask
            if width_bar <= radius*2:
                draw.pieslice((0,0,height_bar, height_bar), 90, 270, fill= 255)
                try:
                    draw.rectangle((radius,0, width_bar, height_bar), fill=255)
                except ValueError:
                    pass
            else:
                draw.rounded_rectangle((0,0,width_bar,height_bar), radius=radius,fill=255)
            rounded_bar = Image.new('RGBA', (width_bar, height_bar), (0,0,0,0))
            rounded_bar.paste(bar, (0,0), mask=mask)
            bar_cords = bar_cords[0] + 10, bar_cords[1]
            white_image.paste(rounded_bar,(cords), mask=mask)
            draw = ImageDraw.Draw(white_image)
            draw.rounded_rectangle((x, y, x+full_width, y+25), radius=radius,outline=0, width=3)
            extra = 40
            font_size = 28
            cords = (x, 170)
            if txt_to_dp == 'Max XP':
                draw = PIL_text_obj(draw, cords, member.display_name,font_size= 80, text_color=(187,155,73))
            else:
                draw = PIL_text_obj(draw, cords, member.display_name,font_size= 80, text_color=(255,255,255))
            draw = PIL_text_obj(draw,bar_cords,percent,font_size=font_size-2)
            if user_stats.stats[member.id]['xp_for_next_rank'] == 'Owner is the highest rank':
                response = 'There is no way to rank up with xp after at this rank.'
            elif type(user_stats.stats[member.id]['xp_for_next_rank']) == str:
                if user_stats.stats[member.id]['xp_for_next_rank'] == 'There is no greater rank beyond Owner':
                    if user_stats.stats[member.id]['rank'] == 'KlasseBot':
                        response = f'There is no higher rank for me.'
                    else:
                        response = f'There is no higher rank.'
                else:
                    response = f'It is not possible to progress with XP.\nIt is only possible to rank up\n{user_stats.stats[member.id]["xp_for_next_rank"]}.'
            else:
                response = f'You need {user_stats.stats[member.id]["xp_for_next_rank"]} xp to rank up to {user_stats.stats[member.id]["next_rank"]}\n(Every message gives 5xp).\n'
            counter = 0
            for split in user_stats.stats[member.id]['join_date'].split('.'):
                if counter == 0:
                    day = str(split)
                elif counter == 1:
                    month = months[split]
                elif counter == 2:
                    year = str(split)
                counter += 1
            date = f'{day} {month} {year}'
            cords = (x, y-50)
            draw = PIL_text_obj(draw, cords, txt_to_dp,font_size= font_size+10)
            cords = cords[0], cords[1] + extra + 60
            draw = PIL_text_obj(draw,cords, f'Messages        {user_stats.stats[member.id]["message_count"]}',font_size= font_size)
            cords = cords[0], cords[1] + extra
            draw = PIL_text_obj(draw,cords, f'Rank                {user_stats.stats[member.id]["rank"]}',font_size= font_size)
            rank_img = user_stats.stats[member.id]["img"]
            rank_img = Path(rank_img) # handels \ and /
            rank_img = rank_img.as_posix()#turns all \ to /
            if not rank_img.startswith('images/'):
                user_stats.stats[member.id]["img"] = f'images/{rank_img}'
                rank_img = f'images/{rank_img}'
            self.server_stats.save_stats
            cords = cords[0], cords[1] + extra
            draw = PIL_text_obj(draw,cords, f'Next rank         {user_stats.stats[member.id]["next_rank"]}',font_size= font_size)
            cords = cords[0], cords[1] + extra
            draw = PIL_text_obj(draw,cords, f'Joined              {date}',font_size= font_size)
            cords = cords[0], cords[1] + extra
            draw = PIL_text_obj(draw,cords, f'Total XP           {user_stats.stats[member.id]["xp"]}',font_size= font_size)
            cords = cords[0], cords[1] + extra
            draw = PIL_text_obj(draw,cords, f'{response}',font_size= font_size)
            
            if rank_img != '':
                try:
                    with Image.open(rank_img, 'r') as rank_img2:
                        rank_img = rank_img2.copy()
                except Exception as e:
                    print(e)
                    rank_img = None
            else:
                rank_img = None
            if rank_img != None:
                extra = 50
                rank_img = rank_img.resize((rank_img.width-extra, rank_img.height-extra))
                if rank_img.size == (300-extra,300-extra):
                    rank_img = rank_img.resize((200,200))
                white_image.paste(rank_img,(85,550), rank_img)#rank_img works as a mask bcs pillow automaticly only uses the alpha channel of the image that it already has
            white_image.resize((500,333), Image.LANCZOS)
            ram = BytesIO()#creates new ram
            white_image.save(ram, format='PNG')#saves it in the ram
            ram.seek(0)
            file = discord.File(fp=ram, filename='stats_card.png')
            await ctx.reply(file=file)
        except discord.Forbidden:
            await ctx.reply('I do not have permissions to send files in this channel.\nIt is probably deactivated for the bot or for everyone to attach files.')
        except Exception as e:
            print(e)
            await ctx.reply('An error occoured while trying to execute this command!')

