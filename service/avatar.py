import cloudinary
import cloudinary.uploader as uploader
from conf.secret import CLOUD_NAME, CLOUD_KEY, CLOUD_SECRET


cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=CLOUD_KEY,
    api_secret=CLOUD_SECRET,
)


def get_uploader():
    """
    The get_uploader function returns the uploader object.
        :returns: The uploader object.


    :return: The uploader function
    :doc-author: Trelent
    """
    return uploader
