# -*- coding: utf-8 -*-

import logging

from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key
access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'

# 要上传的空间
bucket_name = 'avatar'


def storage(data):
    """七牛云存储上传文件接口"""
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name)

        # 上传文件
        ret, info = put_data(token, None, data)

    except Exception as e:
        logging.error(e)
        raise e

    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")

    # 返回七牛中保存的图片名，这个图片名也是访问七牛获取图片的路径
    return ret["key"]


if __name__ == '__main__':
    file = input('请输入文件路径')
    with open(file, 'rb') as f:
        storage(f.read())
