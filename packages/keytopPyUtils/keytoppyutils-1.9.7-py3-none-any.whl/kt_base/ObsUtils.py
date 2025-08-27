from math import trunc

from obs import ObsClient, GetObjectRequest


class ObsUtils:
    def __init__(self,ak,sk,server,bucket_name):
        self.ak = ak
        self.sk = sk
        self.server = server
        self.bucket_name = bucket_name
        self.obsClient = ObsClient(access_key_id=ak, secret_access_key=sk, server=server)

    def upload_file(self,local_path,file_name):
        # 上传对象的附加头域
        #headers = PutObjectHeader()
        # 【可选】待上传对象的MIME类型
        #headers.contentType = 'text/plain'
        #bucketName = "examplebucket"
        # 对象名，即上传后的文件名
        #objectKey = "objectname"
        # 待上传文件/文件夹的完整路径，如aa/bb.txt，或aa/
        #file_path = 'localfile'
        # 上传文件的自定义元数据
        #metadata = {'meta1': 'value1', 'meta2': 'value2'}
        # 文件上传
        resp = self.obsClient.putFile(self.bucket_name, "kyfile/"+file_name, local_path)
        print(resp.status)
        print(resp.body)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            return True
        else:
            return False

    def load_stream(self,file_name):
        # 下载对象的附加请求参数
        getObjectRequest = GetObjectRequest()
        # 获取对象时重写响应中的Content-Type头。
        getObjectRequest.content_type = 'text/plain'
        # 流式下载
        resp = self.obsClient.getObject(bucketName=self.bucket_name, objectKey="kyfile/"+file_name, getObjectRequest=getObjectRequest,
                                   loadStreamInMemory=False)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            return resp.body.response;

    def download_file(self,file_name,local_file_path):
        # 文件下载
        resp = self.obsClient.getObject(self.bucket_name, "kyfile/"+file_name, local_file_path)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            return True
        else:
            return False