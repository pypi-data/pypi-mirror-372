from .request import BBoxRequest
from .constants import HOST_DATA, HOST_CHAT_PIC


__func_info__ = {
    "user_login": {
        "path": "/auth/json",
        "method": "POST",
        "type": 1,
        "token": False,
        "username": True,
        "password": True,
        "certcode": True,
    },
    "user_bind": {"path": "/user/cert/bound/json", "method": "POST", "type": 1, "token": True, "paypwd": True},
    "user_unbind": {"path": "/user/cert/unbound/json", "method": "POST", "type": 1, "token": True, "paypwd": True},
    "user_assets": {"path": "/user/expire/info/json", "method": "GET", "type": 1, "token": True},
    "txn_market_orders_list": {"path": "/transaction/json", "method": "GET", "type": 1, "token": True},
    "txn_seller_orders_list": {"path": "/transaction/seller/json", "method": "GET", "type": 1, "token": True},
    "txn_seller_orders_place": {
        "path": "/transaction/seller/new/json",
        "method": "POST",
        "type": 1,
        "token": True,
        "paypwd": True,
    },
    "txn_seller_orders_confirm": {
        "path": "/transaction/seller/confirm/json",
        "method": "POST",
        "type": 1,
        "token": True,
        "paypwd": True,
    },
    "txn_seller_orders_dispute": {
        "path": "/transaction/dispute/json",
        "method": "POST",
        "type": 1,
        "token": True,
        "paypwd": True,
    },
    "txn_buyer_orders_list": {"path": "/transaction/buyer/json", "method": "GET", "type": 1, "token": True},
    "txn_buyer_orders_place": {"path": "/transaction/buyer/place/json", "method": "GET", "type": 1, "token": True},
    "txn_buyer_orders_payment": {"path": "/transaction/buyer/payment/json", "method": "GET", "type": 1, "token": True},
    "txn_buyer_orders_nopayment": {
        "path": "/transaction/buyer/nopayment/json",
        "method": "GET",
        "type": 1,
        "token": True,
    },
    "txn_buyer_orders_cancel": {"path": "/transaction/buyer/cancel/json", "method": "GET", "type": 1, "token": True},
    "reg_market_orders_list": {"path": "/registration/json", "method": "GET", "type": 1, "token": True},
    "reg_buyer_orders_list": {"path": "/registration/buyer/json", "method": "POST", "type": 1, "token": True},
    "reg_buyer_orders_place": {"path": "/registration/buyer/json", "method": "POST", "type": 1, "token": True},
    "reg_buyer_orders_confirm": {"path": "/registration/buyer/json", "method": "POST", "type": 1, "token": True},
    "reg_buyer_orders_cancel": {"path": "/registration/buyer/json", "method": "POST", "type": 1, "token": True},
    "reg_seller_orders_list": {"path": "/registration/seller/json", "method": "POST", "type": 1, "token": True},
    "reg_seller_orders_place": {
        "path": "/registration/seller/json",
        "method": "POST",
        "type": 1,
        "token": True,
        "paypwd": True,
    },
    "reg_seller_orders_confirm": {"path": "/registration/seller/json", "method": "POST", "type": 1, "token": True},
    "reg_seller_orders_dispute": {
        "path": "/registration/seller/json",
        "method": "POST",
        "type": 1,
        "token": True,
        "paypwd": True,
    },
    "notify_isread": {"path": "/notify/isread/json", "method": "GET", "type": 1, "token": True},
    "notify_remind": {"path": "/notify/remind/json", "method": "GET", "type": 1, "token": True},
    "notify_announce": {"path": "/notify/announce/json", "method": "GET", "type": 1, "token": True},
    "chat": {"path": "/chat/json", "method": "GET", "type": 1, "token": True},
    "chat_list": {"path": "/chat/show/json", "method": "GET", "type": 1, "token": True},
    "chat_send": {"path": "/chat/new/json", "method": "POST", "type": 1, "token": True},
    "chat_pic": {"path": "/chat", "method": "GET", "type": 6, "token": False},
    "user_payment_list": {"path": "/user/payment/json", "method": "GET", "type": 1, "token": True},
    "user_payment_edit": {"path": "user/payment/json", "method": "POST", "type": 1, "token": True, "paypwd": True},
    "user_payment_delete": {"path": "user/payment/json", "method": "POST", "type": 1, "token": True, "paypwd": True},
    "user_payment_new": {"path": "user/payment/json", "method": "POST", "type": 1, "token": True, "paypwd": True},
}


class BeautyBox:
    HOST_DATA = HOST_DATA[0]
    HOST_CHAT_PIC = HOST_CHAT_PIC

    @staticmethod
    def __request__(crypto, typeint, method: str, path: str, **kwargs):
        kwargs.setdefault("domain", BeautyBox.HOST_DATA)
        url = f"https://{kwargs.get('domain')}{path}"
        return BBoxRequest.request(crypto, typeint, method, url, **kwargs)

    @staticmethod
    def user_login(
        crypto, auths: dict, captcha="9d184bc8a496a52cfdc2594f85f2639a", points="26,37", rtype="a", **kwargs
    ):
        path = "/auth/json"
        data = {
            "x5": auths["username"],
            "x7": auths["password"],
            "xi": captcha,
            "xj": points,
            "x1": auths["certcode"],
            "x0": rtype,
        }
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, **kwargs)

    @staticmethod
    def user_bind(crypto, token, auths, **kwargs):
        path = "/user/cert/bound/json"
        data = {"p": auths["paypwd"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def user_unbind(crypto, token, auths, **kwargs):
        path = "/user/cert/unbound/json"
        data = {"p": auths["paypwd"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def user_assets(crypto, token, **kwargs):
        path = "/user/expire/info/json"
        return BeautyBox.__request__(crypto, 1, "GET", path, token=token, **kwargs)

    @staticmethod
    def txn_market_orders_list(crypto, token, rtype, **kwargs):
        path = "/transaction/json"
        params = {"t": rtype}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def txn_seller_orders_list(crypto, token, **kwargs):
        path = "/transaction/seller/json"
        return BeautyBox.__request__(crypto, 1, "GET", path, token=token, **kwargs)

    @staticmethod
    def txn_seller_orders_place(crypto, token, auths, order_type: int, **kwargs):
        path = "/transaction/seller/new/json"
        data = {"t": order_type, "p": auths["paypwd"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def txn_seller_orders_confirm(crypto, token, auths, order_id: int, **kwargs):
        path = "/transaction/seller/confirm/json"
        data = {"p": auths["paypwd"]}
        params = {"id": order_id}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, params=params, token=token, **kwargs)

    @staticmethod
    def txn_seller_orders_dispute(crypto, token, auths, order_id: int, **kwargs):
        path = "/transaction/dispute/json"
        data = {"p": auths["paypwd"]}
        params = {"id": order_id}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, params=params, token=token, **kwargs)

    @staticmethod
    def txn_buyer_orders_list(crypto, token, **kwargs):
        path = "/transaction/buyer/json"
        return BeautyBox.__request__(crypto, 1, "GET", path, token=token, **kwargs)

    @staticmethod
    def txn_buyer_orders_place(crypto, token, order_id: int, **kwargs):
        path = "/transaction/buyer/place/json"
        params = {"id": order_id}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def txn_buyer_orders_payment(crypto, token, order_id: int, **kwargs):
        path = "/transaction/buyer/payment/json"
        params = {"id": order_id}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def txn_buyer_orders_nopayment(crypto, token, order_id: int, **kwargs):
        path = "/transaction/buyer/nopayment/json"
        params = {"id": order_id}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def txn_buyer_orders_cancel(crypto, token, order_id: int, t, **kwargs):
        path = "/transaction/buyer/cancel/json"
        params = {"id": order_id, "t": t}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def reg_market_orders_list(crypto, token, **kwargs):
        path = "/registration/json"
        return BeautyBox.__request__(crypto, 1, "GET", path, token=token, **kwargs)

    @staticmethod
    def reg_buyer_orders_list(crypto, token, **kwargs):
        path = "/registration/buyer/json"
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data = {"x0": "a", "x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def reg_buyer_orders_place(crypto, token, order_id, **kwargs):
        path = "/registration/buyer/json"
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data = {"x6": order_id, "x0": "b", "x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def reg_buyer_orders_confirm(crypto, token, order_id: int, **kwargs):
        path = "/registration/buyer/json"
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data = {"x6": order_id, "x0": "d", "x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def reg_buyer_orders_cancel(crypto, token, order_id: int, **kwargs):
        path = "/registration/buyer/json"
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data = {"x6": order_id, "x0": "f", "x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def reg_seller_orders_list(crypto, token, **kwargs):
        path = "/registration/seller/json"
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data = {"x0": "a", "x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def reg_seller_orders_place(crypto, token, auths, **kwargs):
        path = "/registration/seller/json"
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data = {
            "xa": 0,
            "x9": auths["paypwd"],
            "x0": "b",
            "x2": headers["Device"],
            "x3": int(headers["Os"]),
            "x4": headers["Com"],
        }
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def reg_seller_orders_confirm(crypto, token, order_id: int, **kwargs):
        path = "/registration/seller/json"
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data = {"x6": order_id, "x0": "d", "x2": headers["Device"], "x3": int(headers["Os"]), "x4": headers["Com"]}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def reg_seller_orders_dispute(crypto, token, auths, order_id: int, **kwargs):
        path = "/registration/seller/json"
        headers = BBoxRequest.update_headers(token=token, **kwargs)
        kwargs["headers"] = headers
        data = {
            "x6": order_id,
            "x9": auths["paypwd"],
            "x0": "e",
            "x2": headers["Device"],
            "x3": int(headers["Os"]),
            "x4": headers["Com"],
        }
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def notify_isread(crypto, token, **kwargs):
        path = "/notify/isread/json"
        return BeautyBox.__request__(crypto, 1, "GET", path, token=token, **kwargs)

    @staticmethod
    def notify_remind(crypto, token, page=1, **kwargs):
        path = "/notify/remind/json"
        params = {"page": page}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def notify_announce(crypto, token, page=1, **kwargs):
        path = "/notify/announce/json"
        params = {"page": page}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def chat(crypto, token, **kwargs):
        path = "/chat/json"
        return BeautyBox.__request__(crypto, 1, "GET", path, token=token, **kwargs)

    @staticmethod
    def chat_list(crypto, token, chat_id, page=1, **kwargs):
        path = "/chat/show/json"
        params = {"id": chat_id, "page": page}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def chat_send(crypto, token, chat_id, content, **kwargs):
        path = "/chat/new/json"
        if isinstance(content, bytes):
            image = content.decode()
            data = {"chat_id": chat_id, "image": image, "target": 0}
        else:
            data = {"chat_id": chat_id, "content": content, "target": 0}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, token=token, **kwargs)

    @staticmethod
    def chat_pic(crypto, chat_id, **kwargs):
        path = "/chat"
        params = {"id": chat_id}
        kwargs.setdefault("domain", BeautyBox.HOST_CHAT_PIC)
        return BeautyBox.__request__(crypto, 6, "GET", path, params=params, **kwargs)

    @staticmethod
    def user_payment_list(crypto, token, **kwargs):
        path = "/user/payment/json"
        params = {"ac": "list"}
        return BeautyBox.__request__(crypto, 1, "GET", path, params=params, token=token, **kwargs)

    @staticmethod
    def user_payment_edit(crypto, token, auths, payid, payurl, **kwargs):
        path = "/user/payment/json"
        data = {"account": payurl, "p": auths["paypwd"]}
        params = {"ac": "edit", "id": payid}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, params=params, token=token, **kwargs)

    @staticmethod
    def user_payment_delete(crypto, token, auths: dict, payid, **kwargs):
        path = "/user/payment/json"
        data = {"p": auths["paypwd"]}
        params = {"ac": "del", "id": payid}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, params=params, token=token, **kwargs)

    @staticmethod
    def user_payment_new(crypto, token, auths: dict, aurl, atype, **kwargs):
        path = "/user/payment/json"
        if atype == "alipay":
            account_type = 1
        elif atype == "wxpay":
            account_type = 2
        elif isinstance(atype, int):
            account_type = atype
        else:
            raise ValueError("account_type must be 'alipay', 'wxpay' or int")
        data = {"account": aurl, "t": account_type, "p": auths["paypwd"]}
        params = {"ac": "new"}
        return BeautyBox.__request__(crypto, 1, "POST", path, data=data, params=params, token=token, **kwargs)
