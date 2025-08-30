import re
import json
import requests
import os
import fake_useragent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from concurrent.futures import ThreadPoolExecutor, as_completed
import mimetypes
from urllib.parse import urlparse
from typing import Union, List, Tuple, Dict, Any

try:
    from urlextract import URLExtract
    extractor = URLExtract()
except ImportError:
    extractor = None
    print('[WARNING] urlextract not found or not supported on your python version, regex will be used.')

extractor = None
def image_to_prompt(image_path: Union[str, bytes, List[Union[str, bytes]]], prompt_style: str = 'tag') -> List[Dict[str, Any]]:
    """Send image to vheer.com/image-to-prompt and return the result as a list of dictionaries.
    
    Args:
        image_path (str, bytes, List[Union[str, bytes]]): A file path, URL, bytes or a list of them.
        prompt_style (str, optional): The style of the prompt. Defaults to 'tag'.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the result.
    """

    if not isinstance(image_path, (str, bytes, list)):
        raise TypeError("image_path must be a file path, URL, bytes, or a list of them")
    
    if isinstance(image_path, str):
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                img_data = f.read()
            img_file = ('image.jpg', img_data, mimetypes.guess_type(image_path)[0])
            return [__send_basic_image(img_file, prompt_style)]
        if not extractor:
            pattern = r'https?://[^\'"\\<>|\s,]+'
            if not re.findall(pattern, image_path):
                raise ValueError(f"Invalid URL: {image_path}")
        urls = extractor.find_urls(image_path) if extractor else re.findall(pattern, image_path)
        if not urls:
            raise ValueError(f"No valid URL found in {image_path}")
        return __send_multiple_images(urls, prompt_style)

    if isinstance(image_path, list):
        return __send_multiple_images(image_path, prompt_style)
    elif isinstance(image_path, bytes):
        return __send_basic_image(('image.jpg', image_path, 'image/jpg'), prompt_style)

    raise Exception("Failed to process image")


def get_prompt_styles() -> List[str]:
    """Get the list of available prompt styles.
    
    Returns:
        List[str]: The list of prompt styles.
    """
    return ['tag', 'creative', 'long', 'short']


def __send_basic_image(img_file: Tuple[str, bytes, str], prompt_style: str) -> Dict[str, Any]:
    """Send a single image to vheer.com/image-to-prompt and return the result as a dictionary.
    
    Args:
        img_file (Tuple[str, bytes, str]): A tuple containing the filename, data, and mime type of the image.
        prompt_style (str): The style of the prompt.
    
    Returns:
        Dict[str, Any]: A dictionary containing the result.
    """
    multipart_data = MultipartEncoder(
        fields={
            '1_image': img_file,
            '1_promptStyle': prompt_style,
            '0': '["$K1","n7173352t"]'
        }
    )
    headers = {
        'accept': 'text/x-component',
        'content-type': multipart_data.content_type,
        'next-action': 'fa6112528e902fdca102489e06fea745880f88e3',
        'origin': 'https://vheer.com',
        'referer': 'https://vheer.com/app/image-to-prompt',
        'user-agent': fake_useragent.UserAgent().random
    }
    response = requests.post('https://vheer.com/app/image-to-prompt', headers=headers, data=multipart_data)
    response.raise_for_status()
    return json.loads(response.text.split('1:')[-1])


def __process_single_image(path_or_url: str, prompt_style: str) -> Dict[str, Any]:
    """Process a single image and return the result as a dictionary.
    
    Args:
        path_or_url (str): A file path or URL.
        prompt_style (str): The style of the prompt.
    
    Returns:
        Dict[str, Any]: A dictionary containing the result.
    """
    try:
        if extractor and extractor.has_urls(path_or_url, with_schema_only=True):
            response = requests.get(path_or_url)
            response.raise_for_status()
            img_data = response.content
            image_name = os.path.basename(urlparse(path_or_url).path)
        elif not extractor:
            pattern = r'https?://[^\'"\\<>|\s,]+'
            links = re.findall(pattern, path_or_url)
            if not links:
                raise ValueError(f"No valid URL found in {path_or_url}")
            response = requests.get(links[0])
            response.raise_for_status()
            img_data = response.content
            image_name = os.path.basename(urlparse(links[0]).path)
        else:
            if not os.path.exists(path_or_url):
                raise FileNotFoundError(f"File {path_or_url} not found")
            with open(path_or_url, 'rb') as f:
                img_data = f.read()
            image_name = os.path.basename(path_or_url)

        img_file = (image_name, img_data, mimetypes.guess_type(image_name)[0])
        result = __send_basic_image(img_file, prompt_style)
        return {'image_name': image_name, 'answer_data': result}

    except Exception as e:
        return {'image_name': path_or_url, 'error': str(e)}


def __send_multiple_images(image_paths: List[Union[str, bytes]], prompt_style: str) -> List[Dict[str, Any]]:
    """Send multiple images to vheer.com/image-to-prompt and return the result as a list of dictionaries.
    
    Args:
        image_paths (List[Union[str, bytes]]): A list of file paths or URLs.
        prompt_style (str): The style of the prompt.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the result.
    """
    results = []
    with ThreadPoolExecutor(max_workers=min(5, len(image_paths))) as executor:
        futures = {executor.submit(__process_single_image, path, prompt_style): path for path in image_paths}
        for future in as_completed(futures):
            results.append(future.result())
    return results

image_to_prompt.__version__ = '0.1.0'