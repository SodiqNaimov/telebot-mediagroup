from telebot import TeleBot, types
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio
import threading

bot = TeleBot("Token")

album_data = {}
DEFAULT_DELAY = 0.6


def handle_complete_album(media_group_id, album):
    album.sort(key=lambda msg: msg.date)
    group_elements = []

    for element in album:
        caption_kwargs = {"caption": element.caption} if element.caption else {}
        if element.content_type == "photo":
            input_media = InputMediaPhoto(media=element.photo[-1].file_id, **caption_kwargs)
        elif element.content_type == "video":
            input_media = InputMediaVideo(media=element.video.file_id, **caption_kwargs)
        elif element.content_type == "document":
            input_media = InputMediaDocument(media=element.document.file_id, **caption_kwargs)
        elif element.content_type == "audio":
            input_media = InputMediaAudio(media=element.audio.file_id, **caption_kwargs)
        else:
            bot.send_message(element.chat.id, "This media type isn't supported!")
            return

        group_elements.append(input_media)

    bot.send_media_group(album[0].chat.id, group_elements)


def process_album(media_group_id):
    threading.Timer(DEFAULT_DELAY, lambda: finalize_album(media_group_id)).start()


def finalize_album(media_group_id):
    album = album_data.pop(media_group_id, None)
    if album:
        handle_complete_album(media_group_id, album)


@bot.message_handler(content_types=["photo", "video", "document", "audio"])
def handle_media_messages(message: types.Message):
    media_group_id = message.media_group_id

    if not media_group_id:
        bot.reply_to(message, "This is a single media message.")
        return

    if media_group_id not in album_data:
        album_data[media_group_id] = []
        process_album(media_group_id)

    album_data[media_group_id].append(message)


if __name__ == "__main__":
    bot.infinity_polling()
