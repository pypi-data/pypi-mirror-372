import uuid

class CommonUtils:
    @staticmethod
    def generate_uuid():
        """
        生成一个随机的 UUID (版本 4)

        :return: 生成的 UUID 字符串,已去掉-
        """
        uuid_with_dashes = str(uuid.uuid4())
        uuid_without_dashes = uuid_with_dashes.replace('-', '')
        return uuid_without_dashes

# 使用示例
#uuid_str = CommonUtils.generate_uuid()
#print(f"生成的 UUID: {uuid_str}")