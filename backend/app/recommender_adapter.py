"""Điểm duy nhất app gọi vào recommender.
Có module `recommender` thật (đặt cạnh thư mục app/ hoặc pip install) -> dùng nó, nếu không -> mock.
Module thật cần có: recommend(user_id, k), similar(song_id, k) trả về list[{"song_id","score","reason"}].
"""
try:
    from recommender import recommend, similar  # type: ignore  # lõi thật của bạn kia
    USING_MOCK = False
except ImportError:
    from .mock_recommender import recommend, similar
    USING_MOCK = True

from .mock_recommender import trending  # dùng cho guest
