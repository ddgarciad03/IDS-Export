# NO TELEGRAM VERSION

from git import Repo
import utils as u
import re
from elBarcoTorScraper import *
import asyncio

# TODO encode channel names to latin1. As a woraround, beIN and Barsa now are hardcoded


def cleanse_message(message_content):
    cleansed_content = ""
    rows = [row for row in message_content.split("\n") if len(row.strip()) > 0]
    channel_id_regex = r'[a-zA-Z0-9]{40}'
    if re.search(channel_id_regex, message_content):
        for i, row in enumerate(rows):
            if re.search(channel_id_regex, row):
                if i > 0:
                  cleansed_content += rows[i-1] + "\n" + row + "\n"
                else:
                  cleansed_content += "UNTITLED CHANNEL" + "\n" + row + "\n"
    return cleansed_content


def update_channel_dict(message_content, channel_dict):
    rows = message_content.split("\n")
    for i, row in enumerate(rows):
        if i % 2 == 1:
            channel_id = row
            channel_name = rows[i-1]
            if "DAZN F1 1080" in channel_name:
                channel_name = "DAZN F1 1080"
            elif "DAZN F1 720" in channel_name:
                channel_name = "DAZN F1 720"
            elif "SmartBanck" in channel_name:
                channel_name = channel_name.replace("SmartBanck", "Smartbank")
            elif "La1" in channel_name:
                channel_name = channel_name.replace("La1", "La 1")
            elif "LA 1" in channel_name:
                channel_name = channel_name.replace("LA 1", "La 1")
            elif "Tv" in channel_name:
                channel_name = channel_name.replace("Tv", "TV")
            elif "#0 de Movistar" in channel_name:
                channel_name = channel_name.replace("#0 de Movistar", "#0 M+ HD")

            channel_dict[channel_id] = channel_name
    return channel_dict


def export_channels(channel_dict, export_file):

    channel_list = []

    for channel_id, channel_name in channel_dict.items():
        group_title = u.extract_group_title(channel_name)
        tvg_id = u.extract_tvg_id(channel_name)
        logo = u.get_logo(tvg_id)
        identif = (channel_id[0:4])
        channel_info = {"group_title": group_title,
                        "tvg_id": tvg_id,
                        "logo": logo,
                        "channel_id": channel_id,
                        "channel_name": channel_name + "  " + identif}
        channel_list.append(channel_info)

    all_channels = ""
    # all_channels += '#EXTM3U url-tvg="https://raw.githubusercontent.com/dracohe/CARLOS/master/guide_IPTV.xml"\n'
    all_channels += '#EXTM3U url-tvg="https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guia.xml, https://raw.githubusercontent.com/acidjesuz/EPG/master/guide.xml"\n'

    #channel_pattern = '#EXTINF:-1 group-title="GROUPTITLE" tvg-id="TVGID" tvg-logo="LOGO" ,CHANNELTITLE\nacestream://CHANNELID\n'
    channel_pattern = '#EXTINF:-1 group-title="GROUPTITLE" tvg-id="TVGID" tvg-logo="LOGO" ,CHANNELTITLE\nhttp://127.0.0.1:6878/ace/getstream?id=CHANNELID\n'


    for group_title in u.group_title_order:
        for channel_info in channel_list:
            if channel_info["group_title"] == group_title:
                all_channels += channel_pattern.replace("GROUPTITLE", channel_info["group_title"]) \
                                               .replace("TVGID", channel_info["tvg_id"]) \
                                               .replace("LOGO", channel_info["logo"]) \
                                               .replace("CHANNELID", channel_info["channel_id"]) \
                                               .replace("CHANNELTITLE", channel_info["channel_name"])


    with open(export_file, "w") as f:
        f.write(all_channels)


async def export_messages(export_file = "PATH TO lista.txt"):


        channel_dict = dict()

        try:
            contenido_elBarco = scraper()
            if len(contenido_elBarco) > 0:
                cleansed_content = cleanse_message(contenido_elBarco)
                channel_dict = update_channel_dict(cleansed_content, channel_dict)
        except Exception as e:
            print("elBarcoTorMain : ERROR :", e)

        export_channels(channel_dict, export_file)

        print("elBarcoTorMain : INFO : list exported to local file")


def main():
    asyncio.run(export_messages())

def gitUpdate():
    gitRepo = r'/PATH TO github'
    commitMessage = 'list updated'

    try:
        repo = Repo(gitRepo)
        repo.git.add(update=True)
        repo.index.commit(commitMessage)
        origin = repo.remote(name='origin')
        origin.push()

        print("updating_github : INFO : list updated to github")
    except:
        print("updating_github : ERROR : some error occured while pushing the code")

if __name__ == "__main__":
    main()
    gitUpdate()
