import curl_cffi
import numpy as np
from PIL import Image
import io
import cv2
import random, time, json, os
from bs4 import BeautifulSoup
from rescale_n_crop_img import rescale_short_edge, center_crop
from colors import wait_color, system_color, success_color, error_color, purple_color


headers = {
    "authority": "danbooru.donmai.us",
    "method": "GET",
    "path": "/posts/random",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "priority": "u=0, i",
    "referer": "https://danbooru.donmai.us/",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}



def random_sequence(max_len=32):
    characters = "1234567890qwertyuiopasdfghjklzxcvbnm"
    for _ in range(random.randint(1, 5)):
        characters *= 2
    characters_list = list(characters)
    random.shuffle(characters_list)
    seq = "".join(characters_list)[:max_len]
    return seq



def __get_image_from_danbooru_process(h_tgt=640, w_tgt=384):
    global headers
    response = curl_cffi.get(
        url="https://danbooru.donmai.us/posts/random",
        headers=headers,
        timeout=10,
        allow_redirects=False
    )
    image_post_link = response.headers['location']

    response = curl_cffi.get(
        url=image_post_link,
        headers=headers,
        timeout=10
    )
    soup = BeautifulSoup(response.text, "html.parser")
    image_link = soup.find("img", {"class": "fit-width", "id": "image"})
    if image_link is None:
        return "Ảnh này đã bị gỡ!"
    else:
        image_link = image_link.get("src")

    image_content = curl_cffi.get(
        url=image_link,
        headers=headers
    ).content

    image = np.array(Image.open(io.BytesIO(image_content)).convert("RGB"))
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    h, w, c = image.shape
    if h < w:
       return "Chiều dọc ảnh này nhỏ hơn chiều ngang, không phải ảnh lý tưởng để học pose."

    for i in range(10):
        v = i * 20
        image_ = rescale_short_edge(image, w_tgt + v)
        if image_.shape[0] >= h_tgt:
            image = rescale_short_edge(image, w_tgt + v)
            break
    else:
        return "Kích thước ảnh này không đủ tiêu chí."

    image = center_crop(image, w_tgt, h_tgt)
    return image, image_link


def get_image_from_danbooru(h=640, w=384):
    while True:
        try:
            return __get_image_from_danbooru_process(h, w)
        except:
            print("Đã có lỗi khi crawl ảnh từ danbooru, thử lại sau 5s...")
            time.sleep(5)




def save_images(images: list, images_folder="./danbooru_images_crawled"):
    if not os.path.exists(images_folder):
        os.mkdir(images_folder)
    for image in images:
        cv2.imwrite(images_folder + "/" + random_sequence() + ".jpg", img=image)


def load_logs(log_file="./images_crawled_logs_link.json"):
    if not os.path.exists(log_file):
        with open(log_file, mode="w") as file:
            json.dump([], file, ensure_ascii=False, indent=4)
    with open(log_file, mode="r", encoding="utf-8") as file:
        logs = json.load(fp=file)
    return logs


images_mem_chunking = []
logs_mem_chunking = []
def crawler(h=640, w=384, save_threshold=512, log_file="./images_crawled_logs_link.json", images_folder="./danbooru_images_crawled"):
    global images_mem_chunking
    global logs_mem_chunking

    logs = load_logs(log_file)
    while True:
        crawled = get_image_from_danbooru(h, w)
        if not isinstance(crawled, tuple):
            print(error_color(crawled))
            time.sleep(1)
            continue

        image, link = crawled
        if (link in logs) or (link in logs_mem_chunking):
            print(wait_color("Đã crawl ảnh này rồi, bỏ qua đợi 1s."))
            time.sleep(1)
            continue

        images_mem_chunking.append(image)
        logs_mem_chunking.append(link)
        print(purple_color(f"Đã crawl thành công, tổng ảnh trong bộ nhớ tạm là -> {len(images_mem_chunking)}, đợi 2s để tiếp tục."))
        time.sleep(2)

        if (len(images_mem_chunking) >= save_threshold) or (len(logs_mem_chunking) >= save_threshold):
            logs += logs_mem_chunking
            with open(log_file, mode="w", encoding="utf-8") as file:
                json.dump(obj=logs, fp=file, ensure_ascii=False, indent=4)

            save_images(images_mem_chunking)
            images_num = len(os.listdir(images_folder))

            images_mem_chunking.clear()
            logs_mem_chunking.clear()
            print(success_color(f"Đã lưu các hình ảnh và logs thành công! tổng images đã crawl được là -> {images_num}"))


if __name__ == "__main__":
    crawl = crawler(h=640, w=384, save_threshold=128)